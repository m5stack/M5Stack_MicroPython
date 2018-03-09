/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2018 M5Stack (https://github.com/m5stack)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include "py/obj.h"
#include "driver/i2s.h"
// #include "machine_i2s.h"
#include "py/runtime.h"
#include "py/mperrno.h"

typedef enum {
    I2S, I2S_MERUS, DAC_BUILT_IN, PDM
} output_mode_t;


typedef struct {
    mp_obj_base_t base;
    i2s_port_t port;
    output_mode_t output_mode;
    i2s_config_t config;
    i2s_channel_t num_channels;
    uint8_t volume;
} machine_i2s_obj_t;

extern const mp_obj_type_t machine_i2s_type;


STATIC void machine_i2s_obj_init_helper(machine_i2s_obj_t *self, size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_mode, ARG_bclk, ARG_ws, ARG_data_out, ARG_data_in, ARG_samplerate, ARG_bitdepth, ARG_channel, ARG_volume};
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_mode,         MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = DAC_BUILT_IN} },
        { MP_QSTR_bclk,         MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 2} },
        { MP_QSTR_ws,           MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 13} },
        { MP_QSTR_data_out,     MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 5} },
        { MP_QSTR_data_in,      MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_samplerate,   MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 48000} },
        { MP_QSTR_bitdepth,     MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 16} },
        { MP_QSTR_channel,      MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 2} },
        { MP_QSTR_volume,       MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 80} },
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    output_mode_t mode = args[ARG_mode].u_int;
    self->output_mode = mode;
    self->config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX | (mode == DAC_BUILT_IN ? I2S_MODE_DAC_BUILT_IN : 0));
    self->config.sample_rate = args[ARG_samplerate].u_int;
    self->config.bits_per_sample = args[ARG_bitdepth].u_int;
    self->config.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
    self->config.communication_format = (i2s_comm_format_t)((mode == DAC_BUILT_IN ? 0 : I2S_COMM_FORMAT_I2S) | I2S_COMM_FORMAT_I2S_MSB);
    self->config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,  //Interrupt level 1
    self->config.dma_buf_count = 4;
    self->config.dma_buf_len = 1024;  
    self->config.use_apll = 0;
    self->num_channels = args[ARG_channel].u_int;
    self->volume = args[ARG_volume].u_int;

    if (i2s_driver_install(self->port, &self->config, 0, NULL) != ESP_OK) {
        mp_raise_ValueError("I2S: failed to enable");
    }

    if (mode == DAC_BUILT_IN) {
        i2s_set_pin(self->port, NULL);
        i2s_set_dac_mode(I2S_DAC_CHANNEL_RIGHT_EN);
    } else {
        i2s_pin_config_t pin_config = {
            .bck_io_num = args[ARG_bclk].u_int,
            .ws_io_num = args[ARG_ws].u_int,
            .data_out_num = args[ARG_data_out].u_int,
            .data_in_num = args[ARG_data_in].u_int,
        };
        if (i2s_set_pin(self->port, &pin_config) != ESP_OK) {
            i2s_driver_uninstall(self->port);
            mp_raise_ValueError("I2S: failed to set pins in");
        }
    }

    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);
    // i2s_zero_dma_buffer(self->port);
}

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_int_t port = I2S_NUM_0;
    if (n_args > 0) {
        port = mp_obj_get_int(args[0]);
        n_args--;
        args++;
    }

    if (port >= I2S_NUM_MAX || port < I2S_NUM_0) {
        mp_raise_ValueError("invalid I2S peripheral");
    }

    // Create I2S object
	machine_i2s_obj_t *self = m_new_obj(machine_i2s_obj_t);
	self->base.type = &machine_i2s_type;
	self->port = port;

    mp_map_t kw_args;
    mp_map_init_fixed_table(&kw_args, n_kw, args + n_args);
    machine_i2s_obj_init_helper(self, n_args, args, &kw_args);
    return (machine_i2s_obj_t*)self; // discard const
}

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_init(size_t n_args, const mp_obj_t *args, mp_map_t *kw_args) {
    machine_i2s_obj_init_helper(args[0], n_args - 1, args + 1, kw_args);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_KW(machine_i2s_init_obj, 1, machine_i2s_obj_init);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_deinit(mp_obj_t self_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);
    i2s_driver_uninstall(self->port);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(machine_i2s_deinit_obj, machine_i2s_obj_deinit);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_sample_rates(mp_obj_t self_in, mp_obj_t rate) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->config.sample_rate = mp_obj_get_int(rate);
    i2s_set_sample_rates(self->port, (uint32_t)(self->config.sample_rate));

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_set_sample_rates_obj, machine_i2s_obj_sample_rates);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_bits_per_sample(mp_obj_t self_in, mp_obj_t bits) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->config.bits_per_sample = (i2s_bits_per_sample_t)mp_obj_get_int(bits);
    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_obj_bits_per_sample_obj, machine_i2s_obj_bits_per_sample);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_set_channel(mp_obj_t self_in, mp_obj_t channel) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->num_channels = (i2s_channel_t)mp_obj_get_int(channel);
    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_obj_set_channel_obj, machine_i2s_obj_set_channel);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_set_volume(mp_obj_t self_in, mp_obj_t volume) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->volume = mp_obj_get_int(volume);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_obj_set_volume_obj, machine_i2s_obj_set_volume);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_write(const mp_obj_t self_in, mp_obj_t buf_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf_in, &bufinfo, MP_BUFFER_READ);

    if (i2s_write_bytes(self->port, bufinfo.buf, bufinfo.len, portMAX_DELAY) == ESP_FAIL) {
        mp_raise_OSError(MP_EIO);
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_write_obj, machine_i2s_obj_write);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_obj_stream_out(const mp_obj_t self_in, mp_obj_t buf_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf_in, &bufinfo, MP_BUFFER_READ);

    uint8_t buf_bytes_per_sample = (self->config.bits_per_sample / 8);
    uint32_t num_samples = bufinfo.len / buf_bytes_per_sample / self->num_channels;

    // pointer to left / right sample position
    char *ptr_l = bufinfo.buf;
    char *ptr_r = bufinfo.buf + buf_bytes_per_sample;
    uint8_t stride = buf_bytes_per_sample * 2;

    if (self->num_channels == (i2s_channel_t)1) {
        ptr_r = ptr_l;
    }

    int bytes_pushed = 0;
    TickType_t max_wait = 20 / portTICK_PERIOD_MS; // portMAX_DELAY = bad idea
    for (int i = 0; i < num_samples; i++) {

        if(self->output_mode == DAC_BUILT_IN) {
            // assume 16 bit src bit_depth
            short left = *(short *) ptr_l;
            short right = *(short *) ptr_r;
            left  = (int)left  * self->volume / 100;
            right = (int)right * self->volume / 100;

            // The built-in DAC wants unsigned samples, so we shift the range
            // from -32768-32767 to 0-65535.
            left = left + 0x8000;
            right = right + 0x8000;

            uint32_t sample = (uint16_t) left;
            sample = (sample << 16 & 0xffff0000) | ((uint16_t) right);

            bytes_pushed = i2s_push_sample(self->port, (const char*) &sample, max_wait);
        } else {

            switch (self->config.bits_per_sample)
            {
                case I2S_BITS_PER_SAMPLE_16BIT:
                    ; // workaround

                    /* low - high / low - high */
                    const char samp32[4] = {ptr_l[0], ptr_l[1], ptr_r[0], ptr_r[1]};

                    bytes_pushed = i2s_push_sample(self->port, (const char*) &samp32, max_wait);
                    break;

                case I2S_BITS_PER_SAMPLE_32BIT:
                    ; // workaround

                    const char samp64[8] = {0, 0, ptr_l[0], ptr_l[1], 0, 0, ptr_r[0], ptr_r[1]};
                    bytes_pushed = i2s_push_sample(self->port, (const char*) &samp64, max_wait);
                    break;

                default:
                    // ESP_LOGE(TAG, "bit depth unsupported: %d", self->config.bits_per_sample);
                    mp_raise_ValueError("8 bit depth unsupported");
            }
        }

        // DMA buffer full - retry
        if (bytes_pushed == 0) {
            i--;
        } else {
            ptr_r += stride;
            ptr_l += stride;
        }
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_obj_stream_out_obj, machine_i2s_obj_stream_out);

//----------------------------------------------------------------------
STATIC const mp_rom_map_elem_t machine_i2s_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_init),            MP_ROM_PTR(&machine_i2s_init_obj)},
    { MP_ROM_QSTR(MP_QSTR_deinit),          MP_ROM_PTR(&machine_i2s_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_sample_rate),     MP_ROM_PTR(&machine_i2s_set_sample_rates_obj) },
    { MP_ROM_QSTR(MP_QSTR_bits_per_sample), MP_ROM_PTR(&machine_i2s_obj_bits_per_sample_obj) },
    { MP_ROM_QSTR(MP_QSTR_channel),         MP_ROM_PTR(&machine_i2s_obj_set_channel_obj) },
    { MP_ROM_QSTR(MP_QSTR_volume),          MP_ROM_PTR(&machine_i2s_obj_set_volume_obj) },
    { MP_ROM_QSTR(MP_QSTR_stream_out),      MP_ROM_PTR(&machine_i2s_obj_stream_out_obj) },
    { MP_ROM_QSTR(MP_QSTR_write),           MP_ROM_PTR(&machine_i2s_write_obj) },

    { MP_ROM_QSTR(MP_QSTR_MODE_IN_DAC),     MP_ROM_INT(DAC_BUILT_IN) },
    { MP_ROM_QSTR(MP_QSTR_MODE_I2S),        MP_ROM_INT(I2S) },
    { MP_ROM_QSTR(MP_QSTR_I2S_NUM_0),       MP_ROM_INT(I2S_NUM_0) },
    { MP_ROM_QSTR(MP_QSTR_I2S_NUM_1),       MP_ROM_INT(I2S_NUM_1) },
};

STATIC MP_DEFINE_CONST_DICT(machine_i2s_locals_dict, machine_i2s_locals_dict_table);

const mp_obj_type_t machine_i2s_type = {
    { &mp_type_type },
    .name = MP_QSTR_I2S,
    .make_new = machine_i2s_make_new,
    .locals_dict = (mp_obj_dict_t*)&machine_i2s_locals_dict,
};