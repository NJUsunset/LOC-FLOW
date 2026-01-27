#!/bin/bash

rootdir=${PWD%/*}

seeddir=$rootdir/data_raw/seed/
#seeddir=$rootdir/test

outdir=$rootdir/Data/

if [ ! -e $outdir ];then
	mkdir $outdir
fi

cd $outdir
if [ ! -e ./resp ];then
	mkdir ./resp
fi
if [ ! -e ./st ];then
	mkdir ./st
fi
if [ ! -e ./sac ];then
	mkdir ./sac
fi

evlst=$rootdir/data_raw/evt/hd2001-2023.EQT
cd $seeddir
for file in `ls *.seed`;do
	cd $seeddir
	year=`echo $file | awk '{print substr($1,4,4)}'`
	month=`echo $file | awk '{print substr($1,8,2)}'`
	day=`echo $file | awk '{print substr($1,10,2)}'`
	hour=`echo $file | awk '{print substr($1,12,2)}'`
	mini=`echo $file | awk '{print substr($1,14,2)}'`
	#evtdir=`echo $file | awk -F. '{print $2"."$3}'`
	evtdir=`echo $file | awk -F. '{print $2}'`
	if [ ! -e $outdir/sac/$evtdir ];then
		mkdir $outdir/sac/$evtdir
	fi
	if [ ! -e $outdir/st/$evtdir ];then
                mkdir $outdir/st/$evtdir
        fi
	if [ ! -e $outdir/resp/$evtdir ];then
                mkdir $outdir/resp/$evtdir
        fi
	rdseed -f $file -q $outdir/resp/$evtdir -p -R
	rdseed -f $file -q $outdir/st/$evtdir -S
	rdseed -f $file -d -q $outdir/sac/$evtdir -o 4
	
	cd $outdir/sac/$evtdir
	if [ ! -e mini.seed ];then
		continue
	fi
	mseed2sac mini.seed
	rm mini.seed
	evinfo=`grep "$year$month$day$hour$mini" $evlst`
	sec=`echo $evinfo | awk '{print substr($1,13,2)}'`
	evla=`echo $evinfo | awk '{print $2}'`
	evlo=`echo $evinfo | awk '{print substr($3,1,6)}'`
	mag=`echo $evinfo | awk '{print substr($3,7,4)}'`
	evdp=`echo $evinfo | awk '{print strtonum($4)/1000}'`
# sac <<EOF
# r *.[BS]H[ZNE].00
# w over
# q
# EOF
# rm ./*.[BS]H[ZNE].00

	stlst=$outdir/st/$evtdir/rdseed.stations

	for Zfile in `ls *.00.[BS]HZ.*.SAC`;do
		stn=`echo $Zfile | awk -F. '{print $2}'`
		net=`echo $Zfile | awk -F. '{print $1}'`
		chanZ=`echo $Zfile | awk -F. '{print $4}'`
		chanN=`echo $chanZ | sed 's/HZ/HN/'`
		chanE=`echo $chanZ | sed 's/HZ/HE/'`
		stinfo=`grep "$stn $net" $stlst`
		stlat=`echo $stinfo | awk '{print $3}'`
		stlon=`echo $stinfo | awk '{print $4}'`
		stel=`echo $stinfo | awk '{print $5}'`
		Efile=`echo $Zfile | sed 's/HZ.D.20/HE.D.20/'`
		Nfile=`echo $Zfile | sed 's/HZ.D.20/HN.D.20/'`
		respZ=`ls $outdir/resp/$evtdir/SAC_PZs_"$net"_"$stn"_"$chanZ"_00_*`
		respN=`ls $outdir/resp/$evtdir/SAC_PZs_"$net"_"$stn"_"$chanN"_00_*`
		respE=`ls $outdir/resp/$evtdir/SAC_PZs_"$net"_"$stn"_"$chanE"_00_*`
		# 只取一个文件，避免多匹配
		respZ=$(ls "$outdir/resp/$evtdir"/SAC_PZs_"$net"_"$stn"_"$chanZ"_00_* | head -n 1)
		respN=$(ls "$outdir/resp/$evtdir"/SAC_PZs_"$net"_"$stn"_"$chanN"_00_* | head -n 1)
		respE=$(ls "$outdir/resp/$evtdir"/SAC_PZs_"$net"_"$stn"_"$chanE"_00_* | head -n 1)

		# 读 CONSTANT（用更稳的正则找以 CONSTANT 开头的行）
		constantZ=$(awk '/^CONSTANT/{print $2}' "$respZ")
		constantN=$(awk '/^CONSTANT/{print $2}' "$respN")
		constantE=$(awk '/^CONSTANT/{print $2}' "$respE")

		# 选一个非零的参考常数
		pick=""
		for c in "$constantZ" "$constantN" "$constantE"; do
		if [ -n "$c" ] && [ "$c" != "+0.000000e+00" ]; then
			pick="$c"
			break
		fi
		done

		# 如果找不到可用常数，就别动文件，给个提示
		if [ -z "$pick" ]; then
		echo "WARN: $net.$stn.$chanZ/$chanN/$chanE 都是 0 或缺失，跳过 CONSTANT 修正" >&2
		else
		# 只替换 CONSTANT 行，保留原头、原 poles/zeros
		fix_constant () {
			local f="$1"
			local cur=$(awk '/^CONSTANT/{print $2}' "$f")
			if [ "$cur" = "+0.000000e+00" ] || [ -z "$cur" ]; then
			awk -v newc="$pick" '
				BEGIN{replaced=0}
				/^CONSTANT/ {printf("CONSTANT %s\n", newc); replaced=1; next}
				{print}
				END{if(!replaced){printf("CONSTANT %s\n", newc)}}
			' "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
			echo "INFO: 修正 $f 的 CONSTANT -> $pick"
			fi
		}

		fix_constant "$respZ"
		fix_constant "$respN"
		fix_constant "$respE"
		fi

		
sac <<EOF
r $Zfile
ch cmpaz 0
ch cmpinc 0
rtr;rmean;taper
trans from polezero subtype $respZ to none freq 0.004 0.008 20 40
mul 1.0e9
w over
r $Efile
ch cmpaz 90
ch cmpinc 90
rtr;rmean;taper
trans from polezero subtype $respE to none freq 0.004 0.008 20 40
mul 1.0e9
w over
r $Nfile
ch cmpaz 0
ch cmpinc 90
rtr;rmean;taper
trans from polezero subtype $respN to none freq 0.004 0.008 20 40
mul 1.0e9
w over
r $Zfile $Efile $Nfile
ch o $sec
ch evla $evla
ch evlo $evlo
ch evdp $evdp
ch mag $mag
ch stla $stlat
ch stlo $stlon
ch stel $stel
w over
q
EOF
	done
done
