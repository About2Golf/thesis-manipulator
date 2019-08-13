// Newpma.cpp : Defines the exported functions for the DLL application for use in the Python interface
//
//Vendor ID: 104D
//Product ID: CEC7 (hex string)

//#include "stdafx.h"

#include <string.h>
#include <math.h>
#include "Python.h"
#include <time.h>
//#pragma warning(disable : 4996) // Disable warnings about some functions in VS 2005
//#pragma comment(lib,"usbdll.lib")
#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers
#include <stdio.h>
#include <tchar.h>
#include <conio.h>
#include <process.h>
#include "NewpDLL.h"
#include <typeinfo>

static PyObject *
Py_Init_Sys(PyObject *self, PyObject *args)
{ //opens ALL devices on the USB bus by calling "newp_usb_open_devices"
	//with following parameters: "nProductID=0", "bUseUSBAddress=True"
	//'newp_usb_open_devices' must  be called before any of the other USB functions are called.
	long status = newp_usb_init_system();
	if ( status != 0 ){
		printf("--Error initializing Newport PM.\n");
          return Py_BuildValue("l", status);
	}
	else{
		printf("Newport PM: All USB bus opened.\n");
          return Py_BuildValue("l", status);
	}

}

static PyObject *
Py_Close_Sys(PyObject *self, PyObject *args)
{
//closes all devices on the USB bus
//(no USB communication can occur until "newp_usb_open_devices" is called again)
	newp_usb_uninit_system();
	printf("Newport PM USB Devices closed.\n");
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
Py_Get_DevInfo(PyObject *self, PyObject *args)
{ //retrieves device information for ALL devices on USB bus. Must be called to determine the proper "DeviceID" for ea. open device
	//Return data format:
	//<DeviceID1>,<DeviceDescription1>;<DeviceID2>,<DeviceDescription2>;<DeviceIDX>,<DeviceDescriptionX>
	//Each device MUST be converted to integer for use with "newp_usb_get_ascii" OR "newp_usb_send_ascii"
	//device description data is same response from "*IDN?" query
	//char* Buffer;
     char* Buffer;
	int param = PyArg_ParseTuple(args, "z", &Buffer);
	long status = newp_usb_get_device_info(Buffer);
	if ( status != 0 ){
		printf("Error: Not able to retrieve Newport device info.\n");
          Py_INCREF(Py_None);
        	return Py_None;
	}
	else{
		printf("Successfully retrieved Newport device info.\n");
          return Py_BuildValue("z", Buffer);
	}
	
}

static PyObject *
Py_Send_ASCII(PyObject *self, PyObject *args)
{	//sends the passed in-command to the specified device
	//concatenates a "carriage-return" to the command-string if it does not have one
	long  DeviceID;
	char*  Command;
	int param = PyArg_ParseTuple(args, "ls", &DeviceID, &Command);
	long response = newp_usb_send_ascii(DeviceID, Command, strlen(Command));
	if ( response != 0){
		printf("Write operation failed.\n");
	}
	else{
		printf("Command/query write operation successful.\n");
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
Py_Get_ASCII(PyObject *self, PyObject *args)
{

    long DeviceID;
    char* Buffer;
    unsigned long BytesRead;
    //unsigned long Length;
    int param = PyArg_ParseTuple(args, "lz", &DeviceID,&Buffer);
    //BytesRead = (unsigned long)sizeof(Buffer);
    long response = newp_usb_get_ascii(DeviceID, Buffer,  strlen(Buffer), &BytesRead);
    //long response = 1;
    if ( response != 0){
        printf("Read operation failed.\n");
        printf("DeviceID: %i\n",DeviceID);
        printf("Buffer: %s\n",Buffer);
        Py_INCREF(Py_None);
        return Py_None;
    }
    else{
        printf("Read operation successful.\n");
        return Py_BuildValue("z", Buffer);
    }
    
}

static PyMethodDef Newpma_methods[] = {
    {"Init_Sys", Py_Init_Sys, METH_VARARGS, "Init_Sys()"},
    {"Close_Sys", Py_Close_Sys, METH_VARARGS, "Close_Sys() "},
    {"Get_DevInfo",Py_Get_DevInfo,METH_VARARGS, "Get_DevInfo()"},
    {"Send_ASCII", Py_Send_ASCII,METH_VARARGS, "Send_ASCII()"},
    {"Get_ASCII", Py_Get_ASCII, METH_VARARGS, "Get_ASCII()"},
    {NULL, NULL}

};

PyMODINIT_FUNC
initNewpma(void)
{
	PyObject *pm;
	pm = Py_InitModule("Newpma", Newpma_methods);
}
