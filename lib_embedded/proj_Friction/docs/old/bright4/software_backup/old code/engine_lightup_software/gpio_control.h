#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
 
#define IN  0
#define OUT 1
 
#define LOW  0
#define HIGH 1

#define BUFFER_MAX 3
#define DIRECTION_MAX 35
#define VALUE_MAX 30

#ifndef GPIO_CONTROL_H
#define GPIO_CONTROL_H

int GPIOEnable(int pin);
 
int GPIOUnenable(int pin);
 
int GPIODirection(int pin, int dir);
 
int GPIORead(int pin);
 
//static int GPIOWrite(int pin, int value);

#endif
