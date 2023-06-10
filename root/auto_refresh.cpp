#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <string.h>
#include <dirent.h>

#define MAX_PATH_LEN 1024
#define MAX_CMD_LEN 2048

int install_system_debs() {
    char path[MAX_PATH_LEN]; // ���·�����Ļ�����
    char cmd[MAX_CMD_LEN]; // �������Ļ�����
    int find_debs = 0;

    // ��·��
    DIR* dir = opendir("/root/system_deb/");
    if (dir == NULL) {
        printf("Failed to open directory.\n");
        return 1;
    }

    // ����Ŀ¼�е��ļ�
    struct dirent* dirent;
    while ((dirent = readdir(dir)) != NULL) {
        // ����ļ����� .deb ��β
        if (strcmp(dirent->d_name + strlen(dirent->d_name) - 4, ".deb") == 0) {
            // ��������·����
            snprintf(path, MAX_PATH_LEN, "/root/system_deb/%s", dirent->d_name);

            // ���찲װ����
            snprintf(cmd, MAX_CMD_LEN, "dpkg -i %s", path);

            // ִ�а�װ����
            int ret = system(cmd);
            if (ret != 0) {
                printf("Failed to install package %s.\n", path);
            } else {
                // ɾ����Ӧ��deb�ļ�
                remove(path);
            }
            find_debs = 1;
        }
    }

    // �ر�·��
    closedir(dir);

    return find_debs;
}


int main(int argc, char** argv) {


    while(1)
    {
		sleep(2);
		
		if(install_system_debs())
		{
		  system("sync");
		  system("reboot");
		}
		
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
			install_system_debs();
			system("sync");
			system("dpkg-deb --info /home/mks/armbian-update.deb | grep \"Version:\" > /home/mks/.DebVersion");
			system("rm -rf /home/mks/armbian-update.deb");
			system("reboot");
		}
    
    }
    
    return 0;
}
