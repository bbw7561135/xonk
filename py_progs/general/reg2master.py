#!/usr/bin/env python 

'''

Synopsis:  
    This is a simple program to that makes a master file from the 
    a region file          

Description:  

    Usage:

    reg2master.py regionfile  [masterfile]

    The program requires 1 parameters:

        The name of the regionfile
    
    The program has 1 optional parameter which is the
    name of the master file.  If the optional parameter
    is missing the name will be the same as the regionfile
    with .txt attached


Notes:

                                       
History:
090109    ksl    Coded                                             
111111    ksl    Fixed so would work with pydocs. Routine might 
        be rewritten to make the main routine smaller
190507  ksl Modified to read the color in, because Bill often uses this 
        to indicate something about the source.  This is not currently
        incorporated into master2reg, because I am not sure exactly how
        I want to do this, and because I do not need it currently.


'''

import sys
import os
from astropy.table import Table
import numpy


def radec2deg(ra,dec):
    ''' Convert an ra dec string to degrees.  The string can already
    be in degrees in which case all that happens is a conversion to
    a float'''

    r=ra.split(':')
    d=dec.split(':')

    rr=float(r[0])
    if len(r)>1:
        rr=rr+float(r[1])/60.
    if len(r)>2:
        rr=rr+float(r[2])/3600.
    if len(r)>1:
        rr=15.*rr  # Since we assume ra was in hms
    
    dd=float(d[0])
    x=0
    if len(d)>1:
        x=x+float(d[1])/60.
    if len(d)>2:
        x=x+float(d[2])/3600.
    
    if dd > 0:
        dd=dd+x
    else:
        dd=dd-x
    
    return rr,dd  


def size2arcsec(word):
    '''
    Convert a string to arcsec if possible

    Otherwise return the value
    '''
    if word.count('"')==1: # We have arcsec
        value=float(word.rstrip('"'))
    elif word.count("'")==1: # We have arcsec
        value=60.*float(word.rstrip("'"))
    else:
        print('Error : Could not parse ',word,' to arcsec')
        value=float(word)
    return value

    


def read_regions(filename):
    '''
    read_regions(filename) reads and parses a region file

    170511  ksl Give sources names if they do not have one
    '''
    f=open(filename,'r')
    type='unknown'
    xcolor='unknown'

    records=[]
    source_no=1

    lines=f.readlines()
    for line in lines:
        line=line.replace('(',' ')
        line=line.replace(')',' ')
        line=line.replace('{',' ')
        line=line.replace('}',' ')
        line=line.replace('=',' ')
        line=line.replace(',',' ')
        print(line)
        line=line.split()

        # process a generic line

        if line[0]=='global':
            print('Global:',line)
            j=0
            while j<len(line)-1:
                if line[j]=='color':
                    xcolor=line[j+1]
                j+=1

        # find the name
        j=0
        name='unknown'
        color='unknown'
        while j<len(line)-1:
            if line[j]=='text':
                name=line[j+1]
            if line[j]=='color':
                color=line[j+1]
            j=j+1
        if name=='unknown':
            name='zzz%03d' % source_no
        if color=='unknown':
            color=xcolor



        # Now process circles
        if len(line)==0:
            pass
        elif line[0]=='fk5':
            type='fk5'
        elif line[0]=='image':
            type='image'
        elif line[0]=='physical':
            type='physical'
        elif line[0]=='circle':
            if type=='unknown' or type=='fk5':
                rr,dd=radec2deg(line[1],line[2])
            else:
                rr=float(line[1])
                dd=float(line[2])
            x1=size2arcsec(line[3])
            record=[name,rr,dd,'circle',x1,0.0,0.0,color]
            records=records+[record]
            source_no+=1
        elif line[0]=='ellipse':
            if type=='unknown' or type=='fk5':
                rr,dd=radec2deg(line[1],line[2])
            else:
                rr=float(line[1])
                dd=float(line[2])
            x1=size2arcsec(line[3])
            x2=size2arcsec(line[4])
            theta=float(line[5])
            record=[name,rr,dd,'ellipse',x1,x2,theta,color]
            records=records+[record]
            source_no+=1
        else:
            print('Did not use :',line)
        print(line)
    f.close()
    return type,records




def write_masterfile(masterfile,records,source='unknown',type='unknown'):
    '''
    write a master file

    Notes:

    141102    ksl    Set so that first line was written in a better format 
            for astropy
    '''

    names=['Source_name','RA','Dec','RegType','Major','Minor','Theta','Color']

    x=Table()

    i=0
    while i<len(names):
        value=[]
        for record in records:
            print(record)
            value.append(record[i])
        x[names[i]]=value
        i+=1

    x['RA'].format='10.6f'
    x['Dec'].format='10.6f'
    x['Major'].format='8.2f'
    x['Minor'].format='8.2f'
    x['Theta'].format='8.2f'
    x['Color'].format='10s'

    x.write(masterfile,format='ascii.fixed_width_two_line')

    # f=open(masterfile,'w')

    # f.write('# Masterfile: %s \n' % masterfile)
    # f.write('# Type  %s\n' % type)
    # f.write('      Source_name         RA         Dec      RegType     Major   Minor   Theta \n')

    # i=0
    # while i<len(records):
    #     z=records[i]
    #     # print 'output ',z
    #     f.write('%20s %10.6f %10.6f %10s %8.2f %8.2f %8.2f\n' % (z[0],z[1],z[2],z[3],z[4],z[5],z[6]))
    #     i=i+1
    # f.close()
    return

def doit(regionfile,masterfile=''):
    '''
    Create a master table from a region file
    '''

    if masterfile=='':
        masterfile=regionfile+'.txt'

    print('Regionfile          :', regionfile)
    print('Masterfile          :', masterfile)

    # Finished getting input information

    # read the regionfile

    type,records=read_regions(regionfile)

    print('No of records parsed ', len(records))

    write_masterfile(masterfile,records,regionfile,type)









# Subroutines and function calls are above.  The driving routine is below
if __name__ == "__main__":

    # Read the command line

    argc=len(sys.argv)

    if argc < 2:
        print(__doc__)
        sys.exit()
    elif argc==2:
        doit(sys.argv[1])
    elif argc==3:
        doit(sys.argv[1],sys.argv[2])


