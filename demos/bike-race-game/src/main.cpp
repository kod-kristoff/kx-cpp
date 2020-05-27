#include <iostream>
using namespace std;
#include <sstream>
#include "SDL/SDL.h"
#include "SDL/SDL_image.h"
#include "SDL/SDL_ttf.h"
#include "bike_race/constants.h"
#include "string"
#include "bike_race/coardinate.h"
#include "bike_race/variable.h"
#include "bike_race/init.h"
#include "bike_race/function.h"
#include "bike_race/collision.h"
#include "bike_race/process.h"
#include "bike_race/menu.h"


int main(int ch,char *cha[])
{
     if(!init_all()) 
     {
         std::cout << "init failed." << std::endl;
         return 1;
     }

     if(!load_files()) 
     {
        std::cout << "load_files failed" << std::endl;
        return 1;
     }

     int opt=start_menu();

     std::cout << "start_menu returned: " << opt << std::endl;
     return 0;
}
