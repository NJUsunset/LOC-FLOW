#!/bin/bash -w

#before start, a conda setup is recommended to manage the software dependencies, it can help to avoid possible conflict in python.

#download software
#python software_download.py (can running under base environment of conda, no need to create new environment)

#hypoinverse has to be downloaded seperately at https://www.usgs.gov/software/hypoinverse-earthquake-location
#you may need to manually download it, see possible auto process in software_download.py

#manually go to every software dir and compile them
#compliers in their Makefile may be changed as needed
#you may need to install build-essential and gfortran (linux) or equivalent (mac) to get the compilers

#For phasenet, please install it to "phasenet" virtual envirionment
#conda env create -f env.yml

#build the bin dir
mkdir ../bin

#move commands into ../bin
cp ./FDTCC/bin/FDTCC ../bin/            #need SAC lib in Makefile, remember to change the compiler as needed
cp ./GrowClust/SRC/growclust ../bin/    
cp ./HYPODD/src/hypoDD/hypoDD ../bin/   #change g77 to gfortran or similar complier
cp ./HYPODD/src/ph2dt/ph2dt ../bin/     #change g77 to gfortran or similar complier
cp ./MatchLocate2/bin/* ../bin/         #need SAC lib in Makefile
cp ./REAL/bin/* ../bin/                 #change gcc-10 (on Mac) to gcc as needed
cp ./hyp1.40/source/hyp1.40  ../bin     #change g77 to gfortran or similar complier, you may need patch replace tool to do it. and dont forget to note moving line incase you have same username

#add this commond in your ~/.bash_profile or ~/.bashrc
#export PATH=${your path}/LOC-FLOW/bin/:$PATH
#e.g., export PATH=/Users/miao/Desktop/LOC-FLOW/bin:$PATH

#in your command line
#source ~/.bash_profile
