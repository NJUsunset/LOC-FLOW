import warnings
import os

os.system('git clone https://github.com/Dal-mzhang/REAL.git')
os.system('git clone https://github.com/wayneweiqiang/PhaseNet.git') #Note: it is a new version
os.system('wget http://www.ldeo.columbia.edu/~felixw/HYPODD/HYPODD_1.3.tar.gz -N')
os.system('tar -zxvf HYPODD_1.3.tar.gz')
os.system('rm HYPODD_1.3.tar.gz')
os.system('git clone https://github.com/dttrugman/GrowClust.git')
os.system('git clone https://github.com/Dal-mzhang/MatchLocate2.git')
os.system('git clone https://github.com/MinLiu19/FDTCC')


#hypoinverse can be downloaded at https://www.usgs.gov/software/hypoinverse-earthquake-location
#if download fail please try to manually download the hyp1.40.tar and put it in the current directory
os.system('mkdir hyp1.40')
os.system('cd hyp1.40 && wget https://escweb.wr.usgs.gov/content/software/HYPOINVERSE/hyp1.40.tar -N')
os.system('cd hyp1.40 && tar -xvf hyp1.40.tar && rm hyp1.40.tar')

#Complie each software and move commands in ../bin, and add the path in your ~/.bash_profile
#source ~/.bash_profile