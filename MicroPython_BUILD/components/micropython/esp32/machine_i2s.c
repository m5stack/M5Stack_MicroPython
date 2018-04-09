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
#include "py/objstr.h"
#include "driver/i2s.h"
#include "py/runtime.h"
#include "py/mperrno.h"


typedef struct {
    mp_obj_base_t base;
    i2s_port_t port;
    i2s_config_t config;
    i2s_channel_t num_channels;
    uint16_t volume;
} machine_i2s_obj_t;

extern const mp_obj_type_t machine_i2s_type;


STATIC void machine_i2s_obj_init_helper(machine_i2s_obj_t *self, size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_mode, ARG_rate, ARG_bits, ARG_channel_format, ARG_data_format, ARG_dma_count, ARG_dma_len};
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_mode,           MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_DAC_BUILT_IN} },
        { MP_QSTR_rate,           MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 16000} },
        { MP_QSTR_bits,           MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 16} },
        { MP_QSTR_channel_format, MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = I2S_CHANNEL_FMT_RIGHT_LEFT} },
        { MP_QSTR_data_format,    MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = I2S_COMM_FORMAT_I2S_MSB} },
        { MP_QSTR_dma_count,      MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 4} },
        { MP_QSTR_dma_len,        MP_ARG_KW_ONLY  | MP_ARG_INT, {.u_int = 1024} },
    };
    
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    self->config.mode = (i2s_mode_t)(args[ARG_mode].u_int);
    self->config.sample_rate = (int)args[ARG_rate].u_int;
    self->config.bits_per_sample = (i2s_bits_per_sample_t)args[ARG_bits].u_int;
    self->config.channel_format = (i2s_channel_fmt_t)args[ARG_channel_format].u_int;
    self->config.communication_format = (i2s_comm_format_t)args[ARG_data_format].u_int;
    // self->config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL3,
    self->config.intr_alloc_flags = 0,
    self->config.dma_buf_count = (int)args[ARG_dma_count].u_int;
    self->config.dma_buf_len = (int)args[ARG_dma_len].u_int;
    self->config.use_apll = 0;

    self->num_channels = 2;
    self->volume = 100;

    if (i2s_driver_install(self->port, &self->config, 0, NULL) != ESP_OK) {
        mp_raise_ValueError("I2S: failed to enable");
    }

    if ((self->config.mode & I2S_MODE_DAC_BUILT_IN) || (self->config.mode & I2S_MODE_PDM)) {
        i2s_set_pin(self->port, NULL);
        i2s_set_dac_mode(I2S_DAC_CHANNEL_BOTH_EN); // default
    } 

    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);
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
STATIC mp_obj_t machine_i2s_init(size_t n_args, const mp_obj_t *args, mp_map_t *kw_args) {
    machine_i2s_obj_init_helper(args[0], n_args - 1, args + 1, kw_args);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_KW(machine_i2s_init_obj, 2, machine_i2s_init);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_deinit(mp_obj_t self_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);
    i2s_driver_uninstall(self->port);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(machine_i2s_deinit_obj, machine_i2s_deinit);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_start(mp_obj_t self_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);
    i2s_start(self->port);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(machine_i2s_start_obj, machine_i2s_start);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_stop(mp_obj_t self_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);
    i2s_stop(self->port);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(machine_i2s_stop_obj, machine_i2s_stop);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_sample_rates(mp_obj_t self_in, mp_obj_t rate) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->config.sample_rate = mp_obj_get_int(rate);
    i2s_set_sample_rates(self->port, (uint32_t)(self->config.sample_rate));

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_sample_rates_obj, machine_i2s_sample_rates);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_bits_per_sample(mp_obj_t self_in, mp_obj_t bits) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->config.bits_per_sample = (i2s_bits_per_sample_t)mp_obj_get_int(bits);
    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_bits_per_sample_obj, machine_i2s_bits_per_sample);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_set_channel(mp_obj_t self_in, mp_obj_t channel) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->num_channels = (i2s_channel_t)mp_obj_get_int(channel);
    i2s_set_clk(self->port, self->config.sample_rate, self->config.bits_per_sample, self->num_channels);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_set_channel_obj, machine_i2s_set_channel);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_set_dac_mode(mp_obj_t self_in, mp_obj_t dac_mode) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    uint8_t _dac_mode = mp_obj_get_int(dac_mode);

    if (self->port == I2S_NUM_0) {
        i2s_set_dac_mode((i2s_dac_mode_t)_dac_mode);
    } else {
        mp_raise_ValueError("PDM and built-in DAC functions are only supported on I2S0 for current ESP32 chip.");
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_set_dac_mode_obj, machine_i2s_set_dac_mode);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_set_adc_mode(mp_obj_t self_in, mp_obj_t pin) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    uint8_t adc_pin = mp_obj_get_int(pin);    
    uint8_t adc1_channel[] = {
        ADC1_CHANNEL_4,     /*!< ADC1 channel 4 is GPIO32 */
        ADC1_CHANNEL_5,     /*!< ADC1 channel 5 is GPIO33 */
        ADC1_CHANNEL_6,     /*!< ADC1 channel 6 is GPIO34 */
        ADC1_CHANNEL_7,     /*!< ADC1 channel 7 is GPIO35 */
        ADC1_CHANNEL_0,     /*!< ADC1 channel 0 is GPIO36 */
        ADC1_CHANNEL_1,     /*!< ADC1 channel 1 is GPIO37 */
        ADC1_CHANNEL_2,     /*!< ADC1 channel 2 is GPIO38 */
        ADC1_CHANNEL_3      /*!< ADC1 channel 3 is GPIO39 */
    };

    if (adc_pin < 32 || adc_pin > 39) {
        mp_raise_ValueError("built-in ADC functions are only supported ADC1 channel.");
    }

    if (self->port == I2S_NUM_0) {
        i2s_set_adc_mode(ADC_UNIT_1, (adc1_channel_t)(adc1_channel[adc_pin - 32]));
    } else {
        mp_raise_ValueError("built-in ADC functions are only supported on I2S0 for current ESP32 chip.");
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_set_adc_mode_obj, machine_i2s_set_adc_mode);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_adc_enable(mp_obj_t self_in, mp_obj_t enable) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    uint8_t _enable = mp_obj_get_int(enable);

    if (_enable) {
        i2s_adc_enable(self->port);
    } else {
        i2s_adc_disable(self->port);
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_adc_enable_obj, machine_i2s_adc_enable);

//-------------------------------------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_set_pin(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {

    const mp_arg_t allowed_args[] = {
        { MP_QSTR_bck,  MP_ARG_REQUIRED | MP_ARG_INT, { .u_int = 0 } },
        { MP_QSTR_ws,   MP_ARG_REQUIRED | MP_ARG_INT, { .u_int = 0 } },
        { MP_QSTR_out,  MP_ARG_REQUIRED | MP_ARG_INT, { .u_int = 0 } },
        { MP_QSTR_in,                     MP_ARG_INT, { .u_int = -1 } },
    };
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(pos_args[0]);

	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args - 1, pos_args + 1, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	mp_int_t bck_io_num   = args[0].u_int;
    mp_int_t ws_io_num    = args[1].u_int;
    mp_int_t data_out_num = args[2].u_int;
    mp_int_t data_in_num  = -1;

    if (args[3].u_int >= 0) {
    	data_in_num = args[3].u_int;
    }

    i2s_pin_config_t pin_config = {
        .bck_io_num = bck_io_num,
        .ws_io_num = ws_io_num,
        .data_out_num = data_out_num,
        .data_in_num = data_in_num,
    };

    if (i2s_set_pin(self->port, &pin_config) != ESP_OK) {
        i2s_driver_uninstall(self->port);
        mp_raise_ValueError("I2S: failed to set pins in");
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_KW(machine_i2s_set_pin_obj, 3, machine_i2s_set_pin);

//-----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_set_volume(mp_obj_t self_in, mp_obj_t volume) {
    machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->volume = mp_obj_get_int(volume);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_set_volume_obj, machine_i2s_set_volume);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_read(const mp_obj_t self_in, mp_obj_t buf_len) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    size_t _buf_len = mp_obj_get_int(buf_len);
    vstr_t vstr;
    vstr_init_len(&vstr, _buf_len);

    if (i2s_read_bytes(self->port, (char*)vstr.buf, vstr.len, portMAX_DELAY) == ESP_FAIL) {
        mp_raise_OSError(MP_EIO);
        return mp_const_none;
    }

    // Return read data as string
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_read_obj, machine_i2s_read);

//----------------------------------------------------------------------
STATIC mp_obj_t machine_i2s_write(const mp_obj_t self_in, mp_obj_t buf_in) {
    const machine_i2s_obj_t *self = MP_OBJ_TO_PTR(self_in);

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf_in, &bufinfo, MP_BUFFER_READ);

    // support only 16 bit buffers for now
    if(self->config.bits_per_sample != I2S_BITS_PER_SAMPLE_16BIT) {
        mp_raise_ValueError("support only 16 bit buffers for now");
        return mp_const_none;
    }

    if (self->config.mode & I2S_MODE_DAC_BUILT_IN) {

        uint8_t buf_bytes_per_sample = (self->config.bits_per_sample / 8);
        uint32_t num_samples = bufinfo.len / buf_bytes_per_sample / self->num_channels;

        // pointer to left / right sample position
        char *ptr_l = bufinfo.buf;
        char *ptr_r = bufinfo.buf + buf_bytes_per_sample;
        uint8_t stride = buf_bytes_per_sample * self->num_channels;;

        if (self->num_channels == (i2s_channel_t)1) {
            ptr_r = ptr_l;
        }

        int bytes_pushed = 0;
        TickType_t max_wait = 20 / portTICK_PERIOD_MS; // portMAX_DELAY = bad idea
        for (int i = 0; i < num_samples; i++) {

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

            // DMA buffer full - retry
            if (bytes_pushed == 0) {
                i--;
            } else {
                ptr_l += stride;
                ptr_r += stride;
            }
        }
    } else {

        if (i2s_write_bytes(self->port, bufinfo.buf, bufinfo.len, 0) == ESP_FAIL) 
            mp_raise_OSError(MP_EIO);
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(machine_i2s_write_obj, machine_i2s_write);

//----------------------------------------------------------------------
STATIC const mp_rom_map_elem_t machine_i2s_locals_dict_table[] = {

    // Standard methods
    { MP_ROM_QSTR(MP_QSTR_init),              MP_ROM_PTR(&machine_i2s_init_obj)},
    { MP_ROM_QSTR(MP_QSTR_deinit),            MP_ROM_PTR(&machine_i2s_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_start),             MP_ROM_PTR(&machine_i2s_start_obj) },
    { MP_ROM_QSTR(MP_QSTR_stop),              MP_ROM_PTR(&machine_i2s_stop_obj) },
    { MP_ROM_QSTR(MP_QSTR_sample_rate),       MP_ROM_PTR(&machine_i2s_sample_rates_obj) },
    { MP_ROM_QSTR(MP_QSTR_bits),              MP_ROM_PTR(&machine_i2s_bits_per_sample_obj) },
    { MP_ROM_QSTR(MP_QSTR_nchannels),         MP_ROM_PTR(&machine_i2s_set_channel_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_pin),           MP_ROM_PTR(&machine_i2s_set_pin_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_dac_mode),      MP_ROM_PTR(&machine_i2s_set_dac_mode_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_adc_pin),       MP_ROM_PTR(&machine_i2s_set_adc_mode_obj) },
    { MP_ROM_QSTR(MP_QSTR_adc_enable),        MP_ROM_PTR(&machine_i2s_adc_enable_obj) },
    { MP_ROM_QSTR(MP_QSTR_read),              MP_ROM_PTR(&machine_i2s_read_obj) },
    { MP_ROM_QSTR(MP_QSTR_write),             MP_ROM_PTR(&machine_i2s_write_obj) },
    { MP_ROM_QSTR(MP_QSTR_volume),            MP_ROM_PTR(&machine_i2s_set_volume_obj) },

    // Constants
    { MP_ROM_QSTR(MP_QSTR_I2S_NUM_0),         MP_ROM_INT(I2S_NUM_0) },
    { MP_ROM_QSTR(MP_QSTR_I2S_NUM_1),         MP_ROM_INT(I2S_NUM_1) },

    { MP_ROM_QSTR(MP_QSTR_MODE_MASTER),       MP_ROM_INT(I2S_MODE_MASTER) },
    { MP_ROM_QSTR(MP_QSTR_MODE_SLAVE),        MP_ROM_INT(I2S_MODE_SLAVE) },
    { MP_ROM_QSTR(MP_QSTR_MODE_TX),           MP_ROM_INT(I2S_MODE_TX) },
    { MP_ROM_QSTR(MP_QSTR_MODE_RX),           MP_ROM_INT(I2S_MODE_RX) },
    { MP_ROM_QSTR(MP_QSTR_MODE_DAC_BUILT_IN), MP_ROM_INT(I2S_MODE_DAC_BUILT_IN) },
    { MP_ROM_QSTR(MP_QSTR_MODE_ADC_BUILT_IN), MP_ROM_INT(I2S_MODE_ADC_BUILT_IN) },
    { MP_ROM_QSTR(MP_QSTR_MODE_PDM),          MP_ROM_INT(I2S_MODE_PDM) },

    { MP_ROM_QSTR(MP_QSTR_CHANNEL_RIGHT_LEFT),MP_ROM_INT(I2S_CHANNEL_FMT_RIGHT_LEFT) },
    { MP_ROM_QSTR(MP_QSTR_CHANNEL_ALL_RIGHT), MP_ROM_INT(I2S_CHANNEL_FMT_ALL_RIGHT) },
    { MP_ROM_QSTR(MP_QSTR_CHANNEL_ALL_LEFT),  MP_ROM_INT(I2S_CHANNEL_FMT_ALL_LEFT) },
    { MP_ROM_QSTR(MP_QSTR_CHANNEL_ONLY_RIGHT),MP_ROM_INT(I2S_CHANNEL_FMT_ONLY_RIGHT) },
    { MP_ROM_QSTR(MP_QSTR_CHANNEL_ONLY_LEFT), MP_ROM_INT(I2S_CHANNEL_FMT_ONLY_LEFT) },

    { MP_ROM_QSTR(MP_QSTR_FORMAT_I2S),        MP_ROM_INT(I2S_COMM_FORMAT_I2S) },
    { MP_ROM_QSTR(MP_QSTR_FORMAT_I2S_MSB),    MP_ROM_INT(I2S_COMM_FORMAT_I2S_MSB) },
    { MP_ROM_QSTR(MP_QSTR_FORMAT_I2S_LSB),    MP_ROM_INT(I2S_COMM_FORMAT_I2S_LSB) },
    { MP_ROM_QSTR(MP_QSTR_FORMAT_PCM),        MP_ROM_INT(I2S_COMM_FORMAT_PCM) },
    { MP_ROM_QSTR(MP_QSTR_FORMAT_PCM_SHORT),  MP_ROM_INT(I2S_COMM_FORMAT_PCM_SHORT) },
    { MP_ROM_QSTR(MP_QSTR_FORMAT_PCM_LONG),   MP_ROM_INT(I2S_COMM_FORMAT_PCM_LONG) },

    { MP_ROM_QSTR(MP_QSTR_DAC_DISABLE),       MP_ROM_INT(I2S_DAC_CHANNEL_DISABLE) },
    { MP_ROM_QSTR(MP_QSTR_DAC_RIGHT_EN),      MP_ROM_INT(I2S_DAC_CHANNEL_RIGHT_EN) },
    { MP_ROM_QSTR(MP_QSTR_DAC_LEFT_EN),       MP_ROM_INT(I2S_DAC_CHANNEL_LEFT_EN) },
    { MP_ROM_QSTR(MP_QSTR_DAC_BOTH_EN),       MP_ROM_INT(I2S_DAC_CHANNEL_BOTH_EN) },
};

STATIC MP_DEFINE_CONST_DICT(machine_i2s_locals_dict, machine_i2s_locals_dict_table);

const mp_obj_type_t machine_i2s_type = {
    { &mp_type_type },
    .name = MP_QSTR_I2S,
    .make_new = machine_i2s_make_new,
    .locals_dict = (mp_obj_dict_t*)&machine_i2s_locals_dict,
};
