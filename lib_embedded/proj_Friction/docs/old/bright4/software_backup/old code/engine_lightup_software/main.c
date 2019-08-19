/*
 * newtest.c
 *
 * Copyright (c) 2014 Jeremy Garff <jer @ jers.net>
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted
 * provided that the following conditions are met:
 *
 *     1.  Redistributions of source code must retain the above copyright notice, this list of
 *         conditions and the following disclaimer.
 *     2.  Redistributions in binary form must reproduce the above copyright notice, this list
 *         of conditions and the following disclaimer in the documentation and/or other materials
 *         provided with the distribution.
 *     3.  Neither the name of the owner nor the names of its contributors may be used to endorse
 *         or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


static char VERSION[] = "XX.YY.ZZ";

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <signal.h>
#include <stdarg.h>
#include <getopt.h>
#include <math.h>

#include <dirent.h>


#include "clk.h"
#include "gpio.h"
#include "dma.h"
#include "pwm.h"
#include "version.h"

#include "ws2811.h"

#include "gpio_control.h"

pid_t proc_find(const char* name) 
{
    DIR* dir;
    struct dirent* ent;
    char* endptr;
    char buf[512];

    if (!(dir = opendir("/proc"))) {
        perror("can't open /proc");
        return -1;
    }

    while((ent = readdir(dir)) != NULL) {
        /* if endptr is not a null character, the directory is not
         * entirely numeric, so ignore it */
        long lpid = strtol(ent->d_name, &endptr, 10);
        if (*endptr != '\0') {
            continue;
        }

        /* try to open the cmdline file */
        snprintf(buf, sizeof(buf), "/proc/%ld/cmdline", lpid);
        FILE* fp = fopen(buf, "r");

        if (fp) {
            if (fgets(buf, sizeof(buf), fp) != NULL) {
                /* check the first token in the file, the program name */
                char* first = strtok(buf, " ");
                if (!strcmp(first, name)) {
                    fclose(fp);
                    closedir(dir);
                    return (pid_t)lpid;
                }
            }
            fclose(fp);
        }

    }

    closedir(dir);
    return -1;
}


int proc_count(const char* name)
{
	int count=0;
    DIR* dir;
    struct dirent* ent;
    char* endptr;
    char buf[512];

    if (!(dir = opendir("/proc"))) {
        perror("can't open /proc");
        return -1;
    }

    while((ent = readdir(dir)) != NULL) {
        /* if endptr is not a null character, the directory is not
         * entirely numeric, so ignore it */
        long lpid = strtol(ent->d_name, &endptr, 10);
        if (*endptr != '\0') {
            continue;
        }

        /* try to open the cmdline file */
        snprintf(buf, sizeof(buf), "/proc/%ld/cmdline", lpid);
        FILE* fp = fopen(buf, "r");

        if (fp) {
            if (fgets(buf, sizeof(buf), fp) != NULL) {
                /* check the first token in the file, the program name */
                char* first = strtok(buf, " ");
                if (!strcmp(first, name)) {
                    //fclose(fp);
                    //closedir(dir);
                    //return (pid_t)lpid;
                    count++;
                }
            }
            fclose(fp);
        }

    }

    closedir(dir);
    return count;
}


#define ARRAY_SIZE(stuff)       (sizeof(stuff) / sizeof(stuff[0]))

// defaults for cmdline options
#define TARGET_FREQ             WS2811_TARGET_FREQ
#define GPIO_PIN                18
#define DMA                     10
//#define STRIP_TYPE            WS2811_STRIP_RGB		// WS2812/SK6812RGB integrated chip+leds
//#define STRIP_TYPE              WS2811_STRIP_GBR		// WS2812/SK6812RGB integrated chip+leds
#define STRIP_TYPE            SK6812_STRIP_RGBW		// SK6812RGBW (NOT SK6812RGB)

#define WIDTH                   387
#define HEIGHT                  1
#define LED_COUNT               (WIDTH * HEIGHT)

#define MODE_COLOR		0
#define MODE_WHITE		1
#define MODE_FLOW_SLOW	2
#define MODE_FLOW_FAST	3
#define MODE_STROBE		4

#define SECTION_A_STOP_INDEX		128		// Blue
#define SECTION_B_STOP_INDEX		136		// Green
#define SECTION_C_STOP_INDEX		259		// Blue
#define SECTION_D_STOP_INDEX		289		// Orange
#define SECTION_E_STOP_INDEX		310		// Blue
#define SECTION_F_STOP_INDEX		386		// red

#define COLUMN_A_STOP_INDEX			56		// Blue
#define COLUMN_B_STOP_INDEX			86		// Blue
#define COLUMN_C_STOP_INDEX			128		// Blue
#define COLUMN_D_STOP_INDEX			136		// Green

#define COLUMN_E1_STOP_INDEX		142		// Blue
#define COLUMN_F1_STOP_INDEX		148		// Blue
#define COLUMN_G1_STOP_INDEX		157		// Blue
#define COLUMN_H1_STOP_INDEX		166		// Blue
#define COLUMN_I1_STOP_INDEX		175		// Blue
#define COLUMN_J1_STOP_INDEX		187		// Blue

#define COLUMN_J2_STOP_INDEX		199		// Blue
#define COLUMN_I2_STOP_INDEX		208		// Blue
#define COLUMN_H2_STOP_INDEX		217		// Blue
#define COLUMN_G2_STOP_INDEX		226		// Blue
#define COLUMN_F2_STOP_INDEX		232		// Blue
#define COLUMN_E2_STOP_INDEX		238		// Blue

#define COLUMN_K1_STOP_INDEX		259		// Blue (Blinks w/ K2)
#define COLUMN_L_STOP_INDEX			289		// Orange
#define COLUMN_K2_STOP_INDEX		310		// Blue (Blinks w/ K1)
#define COLUMN_M_STOP_INDEX			340		// Red
#define COLUMN_N_STOP_INDEX			358		// Red
#define COLUMN_O_STOP_INDEX			386		// Red

#define COLUMN_MAX_FILL_COUNT_SLOW 60
#define COLUMN_MAX_FILL_COUNT_FAST 5
static int column_index = 0;
static int column_fill_count = 0;

static double flow_variable = 0.00;
static double flow_variable_dx = 0.05;
static double flow_variable_max = 17.0;

static double slow_flow_variable = 0.00;
static double slow_flow_variable_dx = 0.005;

int width = WIDTH;
int height = HEIGHT;
int led_count = LED_COUNT;

int clear_on_exit = 0;

ws2811_t ledstring =
{
    .freq = TARGET_FREQ,
    .dmanum = DMA,
    .channel =
    {
        [0] =
        {
            .gpionum = GPIO_PIN,
            .count = LED_COUNT,
            .invert = 0,
            .brightness = 255,
            .strip_type = STRIP_TYPE,
        },
        [1] =
        {
            .gpionum = 0,
            .count = 0,
            .invert = 0,
            .brightness = 0,
        },
    },
};

ws2811_led_t *matrix;

static uint8_t running = 1;

int get_mode()
{
	if(GPIORead(5) == 1)
		return MODE_COLOR;

	else if(GPIORead(6) == 1)
		return MODE_WHITE;

	else if(GPIORead(13) == 1)
		return MODE_FLOW_FAST;

	else
		return MODE_STROBE;
}

unsigned long compute_fade(unsigned long value, int fade_setting, int max_fade_setting)
{
	double alpha = ((double) fade_setting) / ((double) max_fade_setting);
	if(alpha > 0.5)
		alpha = fabs(1.0 - alpha);

	double blue = ((double) (value & 0xFF)) * alpha;
	double red = ((double) ((value >> 8) & 0xFF)) * alpha;
	double green = ((double) ((value >> 16) & 0xFF)) * alpha;
	double white = ((double) ((value >> 24) & 0xFF)) * alpha;

	unsigned long new_value = (((int) white) << 24) + (((int) green) << 16) + (((int) red) << 8) + ((int) blue);

	return new_value;
}

unsigned long compute_flow(unsigned long value, double alpha)
{
	double beta = 0.00;
	if(alpha < 0.0)
		beta = 0.00;
	
	else if(alpha >= 0.0 && alpha < 1.0)
		beta = alpha;

	/*else if(alpha >= 1.0 && alpha < 2.0)
		beta = 1.0;

	else if(alpha >= 2.0 && alpha < 3.0)
		beta = (3.0 - alpha);*/

	else
		beta = 1.0;
		//beta = 0.0;

	double blue = ((double) (value & 0xFF)) * beta;
	double red = ((double) ((value >> 8) & 0xFF)) * beta;
	double green = ((double) ((value >> 16) & 0xFF)) * beta;
	double white = ((double) ((value >> 24) & 0xFF)) * beta;

	unsigned long new_value = (((int) white) << 24) + (((int) green) << 16) + (((int) red) << 8) + ((int) blue);
	return new_value;
}

unsigned long compute_transition(unsigned long value1, unsigned long value2, double alpha)
{
	double beta = 0.00;
	if(alpha < 0.0)
		beta = 0.00;
	
	else if(alpha >= 0.0 && alpha < 1.0)
		beta = alpha;
		
	else if(alpha >= 1.0)
		beta = 1.0;

	double blue = ((double) (value1 & 0xFF)) * beta + ((double) (value2 & 0xFF)) * (1.0-beta);
	double red = ((double) ((value1 >> 8) & 0xFF)) * beta + ((double) ((value2 >> 8) & 0xFF)) * (1.0-beta);
	double green = ((double) ((value1 >> 16) & 0xFF)) * beta + ((double) ((value2 >> 16) & 0xFF)) * (1.0-beta);
	double white = ((double) ((value1 >> 24) & 0xFF)) * beta + ((double) ((value2 >> 24) & 0xFF)) * (1.0-beta);

	unsigned long new_value = (((int) white) << 24) + (((int) green) << 16) + (((int) red) << 8) + ((int) blue);
	return new_value;
}

unsigned long compute_sweep(unsigned long value, double alpha)
{
	double beta = 0.00;
	if(alpha < 0.0)
		beta = 0.00;
	
	else if(alpha >= 0.0 && alpha < 1.0)
		beta = alpha;

	else if(alpha >= 1.0 && alpha < 3.0)
		beta = 1.0;

	else if(alpha >= 3.0 && alpha <  4.0)
		beta = (4.0 - alpha);

	else if(alpha >= 3.0)
		beta = 0.0;

	double blue = ((double) (value & 0xFF)) * beta;
	double red = ((double) ((value >> 8) & 0xFF)) * beta;
	double green = ((double) ((value >> 16) & 0xFF)) * beta;
	double white = ((double) ((value >> 24) & 0xFF)) * beta;

	unsigned long new_value = (((int) white) << 24) + (((int) green) << 16) + (((int) red) << 8) + ((int) blue);
	return new_value;
}

unsigned long compute_flash(unsigned long value1, unsigned long value2, double alpha)
{
	double beta = 0.5*(round(cos(alpha*M_PI))+1.0);
	
	double blue = ((double) (value1 & 0xFF)) * beta + ((double) (value2 & 0xFF)) * (1.0-beta);
	double red = ((double) ((value1 >> 8) & 0xFF)) * beta + ((double) ((value2 >> 8) & 0xFF)) * (1.0-beta);
	double green = ((double) ((value1 >> 16) & 0xFF)) * beta + ((double) ((value2 >> 16) & 0xFF)) * (1.0-beta);
	double white = ((double) ((value1 >> 24) & 0xFF)) * beta + ((double) ((value2 >> 24) & 0xFF)) * (1.0-beta);

	unsigned long new_value = (((int) white) << 24) + (((int) green) << 16) + (((int) red) << 8) + ((int) blue);
	return new_value;
}

double compute_transition_profile(double t)
{
	return (0.1 + 15.2*t - 66.7*t*t + 97.1*t*t*t - 45.6*t*t*t*t)/1.2;
}

void matrix_render(void)
{    
	int current_mode = get_mode();

	if(current_mode == MODE_WHITE)
	{
		for(int i=0; i<LED_COUNT; i++)
			ledstring.channel[0].leds[i] = 0xFF000000;
	}
	
	else if(current_mode == MODE_COLOR)
	{
		for(int i=0; i<LED_COUNT; i++)
		{
			if(i <= SECTION_A_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x000000FF;
				
			else if(i <= SECTION_B_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x00FF0000;
			
			else if(i <= SECTION_C_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x000000FF;
			
			else if(i <= SECTION_D_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x000FFF00;
			
			else if(i <= SECTION_E_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x000000FF;
			
			else if(i <= SECTION_F_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x0000FF00;
		}
	}

	else if(current_mode == MODE_FLOW_SLOW)// || current_mode == MODE_FLOW_FAST)
	{
		int column_max_fill_count = 1;
		if(current_mode == MODE_FLOW_SLOW)
			column_max_fill_count = COLUMN_MAX_FILL_COUNT_SLOW;

		else if(current_mode == MODE_FLOW_FAST)
			column_max_fill_count = COLUMN_MAX_FILL_COUNT_FAST;
		
		// Turn off all LEDs
		for(int i=0; i<LED_COUNT; i++)
			ledstring.channel[0].leds[i] = 0x00000000;

		// Turn on LEDs except for blink column
		for(int i=0; i<LED_COUNT; i++)
		{
			if(i <= COLUMN_A_STOP_INDEX)
			{
				if(column_index == 0)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_B_STOP_INDEX)
			{
				if(column_index == 1)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_C_STOP_INDEX)
			{
				if(column_index == 2)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_D_STOP_INDEX)
			{
				//if(column_index == 3)
				//ledstring.channel[0].leds[i] = 0x00FF0000;
			}

			else if(i <= COLUMN_E1_STOP_INDEX)
			{
				if(column_index == 4)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_F1_STOP_INDEX)
			{
				if(column_index == 5)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_G1_STOP_INDEX)
			{
				if(column_index == 6)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_H1_STOP_INDEX)
			{
				if(column_index == 7)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_I1_STOP_INDEX)
			{
				if(column_index == 8)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_J1_STOP_INDEX)
			{
				if(column_index == 9)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_J2_STOP_INDEX)
			{
				if(column_index == 9)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_I2_STOP_INDEX)
			{
				if(column_index == 8)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_H2_STOP_INDEX)
			{
				if(column_index == 7)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_G2_STOP_INDEX)
			{
				if(column_index == 6)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_F2_STOP_INDEX)
			{
				if(column_index == 5)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_E2_STOP_INDEX)
			{
				if(column_index == 4)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_K1_STOP_INDEX)
			{
				if(column_index == 10)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_L_STOP_INDEX)
			{
				if(column_index == 11)
					ledstring.channel[0].leds[i] = compute_fade(0x000FFF00, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000FFF00;
			}

			else if(i <= COLUMN_K2_STOP_INDEX)
			{
				if(column_index == 10)
					ledstring.channel[0].leds[i] = compute_fade(0x000000FF, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x000000FF;
			}

			else if(i <= COLUMN_M_STOP_INDEX)
			{
				if(column_index == 12)
					ledstring.channel[0].leds[i] = compute_fade(0x0000FF00, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x0000FF00;
			}

			else if(i <= COLUMN_N_STOP_INDEX)
			{
				if(column_index == 13)
					ledstring.channel[0].leds[i] = compute_fade(0x0000FF00, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x0000FF00;
			}

			else if(i <= COLUMN_O_STOP_INDEX)
			{
				if(column_index == 14)
					ledstring.channel[0].leds[i] = compute_fade(0x0000FF00, column_fill_count, column_max_fill_count);
					//ledstring.channel[0].leds[i] = 0x0000FF00;
			}
		}
		
		column_fill_count++;
		if(column_fill_count == column_max_fill_count)
		{
			column_index++;
			if(column_index == 3)
				column_index++;
			
			else if(column_index == 15)
				column_index = 0;

			column_fill_count = 0;
		}
	}
		
	else if(current_mode == MODE_FLOW_FAST)
	{
		// Turn off all LEDs
		for(int i=0; i<LED_COUNT; i++)
			ledstring.channel[0].leds[i] = 0x00000000;

		// Turn on LEDs except for blink column
		for(int i=0; i<LED_COUNT; i++)
		{
			if(i <= COLUMN_A_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable);
			}

			else if(i <= COLUMN_B_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-1.0);
			}

			else if(i <= COLUMN_C_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-2.0);
			}

			else if(i <= COLUMN_D_STOP_INDEX)
			{
				//if(column_index == 3)
				ledstring.channel[0].leds[i] = 0x00FF0000;
			}

			else if(i <= COLUMN_E1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-3.0);
			}

			else if(i <= COLUMN_F1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-4.0);
			}

			else if(i <= COLUMN_G1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-5.0);
			}

			else if(i <= COLUMN_H1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-6.0);
			}

			else if(i <= COLUMN_I1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-7.0);
			}

			else if(i <= COLUMN_J1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-8.0);
			}

			else if(i <= COLUMN_J2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-8.0);
			}

			else if(i <= COLUMN_I2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-7.0);
			}

			else if(i <= COLUMN_H2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-6.0);
			}

			else if(i <= COLUMN_G2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-5.0);
			}

			else if(i <= COLUMN_F2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-4.0);
			}

			else if(i <= COLUMN_E2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-3.0);
			}

			else if(i <= COLUMN_K1_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-9.0);
			}

			else if(i <= COLUMN_L_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000FFF00, flow_variable-10.0);
			}

			else if(i <= COLUMN_K2_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x000000FF, flow_variable-9.0);
			}

			else if(i <= COLUMN_M_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x0000FF00, flow_variable-11.0);
			}

			else if(i <= COLUMN_N_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x0000FF00, flow_variable-12.0);
			}

			else if(i <= COLUMN_O_STOP_INDEX)
			{
				ledstring.channel[0].leds[i] = compute_flow(0x0000FF00, flow_variable-13.0);
			}
		}

		flow_variable += flow_variable_dx;
		if(flow_variable > flow_variable_max)
			flow_variable = 0.00;
	}


	else if(current_mode == MODE_STROBE)
	{
		// Turn off all LEDs
		for(int i=0; i<LED_COUNT; i++)
			ledstring.channel[0].leds[i] = 0x00000000;

		// Turn on LEDs except for blink column
		for(int i=0; i<LED_COUNT; i++)
		{
			if(i <= COLUMN_A_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable);

			else if(i <= COLUMN_B_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-1.0);

			else if(i <= COLUMN_C_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-2.0);

			else if(i <= COLUMN_D_STOP_INDEX)
				ledstring.channel[0].leds[i] = 0x00FF0000;

			else if(i <= COLUMN_E1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-3.0);

			else if(i <= COLUMN_F1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-4.0);

			else if(i <= COLUMN_G1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-5.0);

			else if(i <= COLUMN_H1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-6.0);

			else if(i <= COLUMN_I1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-7.0);

			else if(i <= COLUMN_J1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-8.0);

			else if(i <= COLUMN_J2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-8.0);

			else if(i <= COLUMN_I2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-7.0);

			else if(i <= COLUMN_H2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-6.0);

			else if(i <= COLUMN_G2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-5.0);

			else if(i <= COLUMN_F2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-4.0);

			else if(i <= COLUMN_E2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_sweep(0x000000FF, flow_variable-3.0);

			else if(i <= COLUMN_K1_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_flash(0x000000FF, 0x0000FFFF, 0.5*flow_variable);

			else if(i <= COLUMN_L_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_flash(0x000FFF00, 0x00001010, 0.5*flow_variable);

			else if(i <= COLUMN_K2_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_flash(0x000000FF, 0x0000FFFF, 0.5*flow_variable);

			//else if(i <= COLUMN_M_STOP_INDEX)
			//	ledstring.channel[0].leds[i] = compute_transition(0x0000FF00, 0x000FFF00, slow_flow_variable);
				//ledstring.channel[0].leds[i] = compute_sweep(0x0000FF00, 0.5*flow_variable);

			//else if(i <= COLUMN_N_STOP_INDEX)
			//	ledstring.channel[0].leds[i] = compute_transition(0x00000000, 0x0000FFF00, slow_flow_variable);
				//ledstring.channel[0].leds[i] = compute_sweep(0x0000FF00, 0.5*flow_variable-1.0);

			else if(i <= COLUMN_O_STOP_INDEX)
				ledstring.channel[0].leds[i] = compute_transition(0x0000FF00, 0x00000000, compute_transition_profile(slow_flow_variable));
				//ledstring.channel[0].leds[i] = compute_transition(0x0000FF00, 0x00000000, (0.1 + 15.2*slow_flow_variable - 66.7*pow(slow_flow_variable,2.0) + 97.1*pow(slow_flow_variable,3.0) - 45.6*pow(slow_flow_variable,4.0))/1.2);
				//ledstring.channel[0].leds[i] = compute_sweep(0x0000FF00, 0.5*flow_variable-2.0);
		}
		
		flow_variable += flow_variable_dx*20.0;
		if(flow_variable > 10.0)
			flow_variable = 0.00;
		
		slow_flow_variable += slow_flow_variable_dx;
		if(slow_flow_variable > 1.0)
			slow_flow_variable = 0.00;
	}
}

void matrix_raise(void)
{
    int x, y;

    for (y = 0; y < (height - 1); y++)
    {
        for (x = 0; x < width; x++)
        {
            // This is for the 8x8 Pimoroni Unicorn-HAT where the LEDS in subsequent
            // rows are arranged in opposite directions
            matrix[y * width + x] = matrix[(y + 1)*width + width - x - 1];
        }
    }
}

void matrix_clear(void)
{
    /*int x, y;

    for (y = 0; y < (height ); y++)
    {
        for (x = 0; x < width; x++)
        {
            matrix[y * width + x] = 0;
        }
    }*/
    for(int i=0; i<LED_COUNT; i++)
    {
		ledstring.channel[0].leds[i] = 0x00000000;
	}
}

int dotspos[] = { 0, 1, 2, 3, 4, 5, 6, 7 };
ws2811_led_t dotcolors[] =
{
    0x00200000,  // red
    0x00201000,  // orange
    0x00202000,  // yellow
    0x00002000,  // green
    0x00002020,  // lightblue
    0x00000020,  // blue
    0x00100010,  // purple
    0x00200010,  // pink
};

ws2811_led_t dotcolors_rgbw[] =
{
    0x00200000,  // red
    0x10200000,  // red + W
    0x00002000,  // green
    0x10002000,  // green + W
    0x00000020,  // blue
    0x10000020,  // blue + W
    0x00101010,  // white
    0x10101010,  // white + W

};

void matrix_bottom(void)
{
    int i;

    for (i = 0; i < (int)(ARRAY_SIZE(dotspos)); i++)
    {
        dotspos[i]++;
        if (dotspos[i] > (width - 1))
        {
            dotspos[i] = 0;
        }

        if (ledstring.channel[0].strip_type == SK6812_STRIP_RGBW) {
            matrix[dotspos[i] + (height - 1) * width] = dotcolors_rgbw[i];
        } else {
            matrix[dotspos[i] + (height - 1) * width] = dotcolors[i];
        }
    }
}

static void ctrl_c_handler(int signum)
{
	(void)(signum);
    running = 0;
}

static void setup_handlers(void)
{
    struct sigaction sa =
    {
        .sa_handler = ctrl_c_handler,
    };

    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
}


void parseargs(int argc, char **argv, ws2811_t *ws2811)
{
	int index;
	int c;

	static struct option longopts[] =
	{
		{"help", no_argument, 0, 'h'},
		{"dma", required_argument, 0, 'd'},
		{"gpio", required_argument, 0, 'g'},
		{"invert", no_argument, 0, 'i'},
		{"clear", no_argument, 0, 'c'},
		{"strip", required_argument, 0, 's'},
		{"height", required_argument, 0, 'y'},
		{"width", required_argument, 0, 'x'},
		{"version", no_argument, 0, 'v'},
		{0, 0, 0, 0}
	};

	while (1)
	{

		index = 0;
		c = getopt_long(argc, argv, "cd:g:his:vx:y:", longopts, &index);

		if (c == -1)
			break;

		switch (c)
		{
		case 0:
			/* handle flag options (array's 3rd field non-0) */
			break;

		case 'h':
			fprintf(stderr, "%s version %s\n", argv[0], VERSION);
			fprintf(stderr, "Usage: %s \n"
				"-h (--help)    - this information\n"
				"-s (--strip)   - strip type - rgb, grb, gbr, rgbw\n"
				"-x (--width)   - matrix width (default 8)\n"
				"-y (--height)  - matrix height (default 8)\n"
				"-d (--dma)     - dma channel to use (default 5)\n"
				"-g (--gpio)    - GPIO to use\n"
				"                 If omitted, default is 18 (PWM0)\n"
				"-i (--invert)  - invert pin output (pulse LOW)\n"
				"-c (--clear)   - clear matrix on exit.\n"
				"-v (--version) - version information\n"
				, argv[0]);
			exit(-1);

		case 'D':
			break;

		case 'g':
			if (optarg) {
				int gpio = atoi(optarg);
/*
	PWM0, which can be set to use GPIOs 12, 18, 40, and 52.
	Only 12 (pin 32) and 18 (pin 12) are available on the B+/2B/3B
	PWM1 which can be set to use GPIOs 13, 19, 41, 45 and 53.
	Only 13 is available on the B+/2B/PiZero/3B, on pin 33
	PCM_DOUT, which can be set to use GPIOs 21 and 31.
	Only 21 is available on the B+/2B/PiZero/3B, on pin 40.
	SPI0-MOSI is available on GPIOs 10 and 38.
	Only GPIO 10 is available on all models.

	The library checks if the specified gpio is available
	on the specific model (from model B rev 1 till 3B)

*/
				ws2811->channel[0].gpionum = gpio;
			}
			break;

		case 'i':
			ws2811->channel[0].invert=1;
			break;

		case 'c':
			clear_on_exit=1;
			break;

		case 'd':
			if (optarg) {
				int dma = atoi(optarg);
				if (dma < 14) {
					ws2811->dmanum = dma;
				} else {
					printf ("invalid dma %d\n", dma);
					exit (-1);
				}
			}
			break;

		case 'y':
			if (optarg) {
				height = atoi(optarg);
				if (height > 0) {
					ws2811->channel[0].count = height * width;
				} else {
					printf ("invalid height %d\n", height);
					exit (-1);
				}
			}
			break;

		case 'x':
			if (optarg) {
				width = atoi(optarg);
				if (width > 0) {
					ws2811->channel[0].count = height * width;
				} else {
					printf ("invalid width %d\n", width);
					exit (-1);
				}
			}
			break;

		case 's':
			if (optarg) {
				if (!strncasecmp("rgb", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_RGB;
				}
				else if (!strncasecmp("rbg", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_RBG;
				}
				else if (!strncasecmp("grb", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_GRB;
				}
				else if (!strncasecmp("gbr", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_GBR;
				}
				else if (!strncasecmp("brg", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_BRG;
				}
				else if (!strncasecmp("bgr", optarg, 4)) {
					ws2811->channel[0].strip_type = WS2811_STRIP_BGR;
				}
				else if (!strncasecmp("rgbw", optarg, 4)) {
					ws2811->channel[0].strip_type = SK6812_STRIP_RGBW;
				}
				else if (!strncasecmp("grbw", optarg, 4)) {
					ws2811->channel[0].strip_type = SK6812_STRIP_GRBW;
				}
				else {
					printf ("invalid strip %s\n", optarg);
					exit (-1);
				}
			}
			break;

		case 'v':
			fprintf(stderr, "%s version %s\n", argv[0], VERSION);
			exit(-1);

		case '?':
			/* getopt_long already reported error? */
			exit(-1);

		default:
			exit(-1);
		}
	}
}


int main(int argc, char *argv[])
{
	// Check if this program is already running
	/*FILE* handle = fopen("/var/run_engine_lights", "r");
	if(handle != NULL)
	{
		printf("Error: Program already running...\n");
		return 0;
	}

	handle = fopen("/var/run_engine_lights", "w");
	fclose(handle);*/
	if(proc_count("/home/pi/Desktop/engine_lightup_software/test") > 1)
	{
		printf("Error: Program already running...\n");
		return 0;
	}
	
	// Initialize Neopixel library
    ws2811_return_t ret;

    sprintf(VERSION, "%d.%d.%d", VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO);

    parseargs(argc, argv, &ledstring);

    matrix = malloc(sizeof(ws2811_led_t) * width * height);

    setup_handlers();

    if ((ret = ws2811_init(&ledstring)) != WS2811_SUCCESS)
    {
        fprintf(stderr, "ws2811_init failed: %s\n", ws2811_get_return_t_str(ret));
        return ret;
    }
    
    // Initialize GPIO
    GPIOEnable(5); GPIODirection(5, 0);
    GPIOEnable(6); GPIODirection(6, 0);
    GPIOEnable(13); GPIODirection(13, 0);
    GPIOEnable(19); GPIODirection(19, 0);

	int last_mode = get_mode();

	// Main loob
    while (running)
    {
		if(get_mode() != last_mode)
		{
			column_index = 0;
			column_fill_count = 0;
			
			flow_variable = 0.00;
		}
		last_mode = get_mode();
		
        matrix_raise();
        matrix_bottom();
        matrix_render();

        if ((ret = ws2811_render(&ledstring)) != WS2811_SUCCESS)
        {
            fprintf(stderr, "ws2811_render failed: %s\n", ws2811_get_return_t_str(ret));
            break;
        }

        // 15 frames /sec
        usleep(1000000 / 60);
    
		//printf("%d %d %d %d\n", GPIORead(5), GPIORead(6), GPIORead(13), GPIORead(19));
    }

	// Uninitialize Neopixel library
    if (clear_on_exit)
    {
		matrix_clear();
		//matrix_render();
		ws2811_render(&ledstring);
    }

    ws2811_fini(&ledstring);

    printf ("\n");
    
    // Uninitialize GPIO
    GPIOUnenable(5);
    GPIOUnenable(6);
    GPIOUnenable(13);
    GPIOUnenable(19);

	// Free up program so it can run again
	/*if(remove("/var/run_engine_lights") != 0)
	{
		printf("Error: Could not remove /var/run_engine_lights\n");
		return 0;
	}*/
    
    return ret;
}
