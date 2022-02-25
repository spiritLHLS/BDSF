#!/bin/bash
# -*- coding: utf8 -*-
cd /Date-iterms/BDSF
sudo su ubuntu
sudo kill -9 $(pidof Xtightvnc)
sudo kill -9 $(pidof Firefox)
#sudo git add -A
#sudo git commit -am "auto save"
#sudo git push -f origin master