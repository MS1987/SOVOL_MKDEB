#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <string.h>


int main(int argc, char** argv) {


    while(1)
    {
		sleep(2);
		if (access("/dev/sda", F_OK) == 0) 
		{
			if (access("/dev/sda1", F_OK) == 0) 
			{
				if (access("/home/mks/printer_data/gcodes/USB", F_OK) != 0) 
				{
					system("/usr/bin/systemctl --no-block restart makerbase-automount@sda1.service");
				
				   continue;
				}
			}
				  
		}

		if(access("/home/mks/printer_data/gcodes/USB/armbian-update.deb", F_OK) == 0)
		{
			//find the update deb file
			if (access("/home/mks/printer_data/gcodes/USB/factory_mode", F_OK) == 0) 
			{
				system("cp /home/mks/printer_data/gcodes/USB/armbian-update.deb /home/mks/armbian-update.deb -f");
			}
			else
			{
				system("mv /home/mks/printer_data/gcodes/USB/armbian-update.deb /home/mks/armbian-update.deb -f");
			}
		}
		
		if(access("/home/mks/armbian-update.deb", F_OK) == 0)
		{
			sleep(1);
			system("dpkg -i /home/mks/armbian-update.deb");
			system("sync");
			system("dpkg-deb --info /home/mks/armbian-update.deb | grep \"Version:\" > /home/mks/.DebVersion");
			system("rm -rf /home/mks/armbian-update.deb");
			system("reboot");
		}
    }
    
    return 0;
}
