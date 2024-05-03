# convert xml into par format
#
# ----- VERSION HISTORY -----
#
# Version 0.1 - 14, October 2015
#       - 1st Beta Release
# Version 0.2 - 22, October 2015
#       - reverse translation of patient positioning (beyond HFS-->Head First Supine)
#       - reverse translation of phase encode directions (beyond AP-->Anterior-Posterior)
#       - reverse translation of image type
#       - reverse translation of sequence type
#       - reverse translation of "info" tags (Display Orientation, Slice Orientation, fMRI Status Indication, Image Type Ed Es)
#       - reverse translation of contrast type
#       - reverse translation of anisotropy direction
#       - reverse translation of label type
#       - crop string condition inlcuded in form_str_len
#
# ----- LICENSE -----                 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License (GPL) as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version. For more detail see the 
#    GNU General Public License at <http://www.gnu.org/licenses/>.
#    additionally to the GPL the following license terms apply:
#
#    1) Personal NO MILTARY clause:
#    THE USE OF THIS SOFTWARE OR ANY PARTS OF IT IS EXPLICITLY PROHIBITED FOR
#    MILITARY INSTITUTIONS, BOTH GOVERNMENTAL AND PRIVATE "SECURITY" SERVICES, 
#    AND ANY INSTITUTIONS DIRECTLY OR INDIRECTLY LINKED TO INTELLIGENCE SERVICES, 
#    BOTH FOR MILITARY AND CIVIL ESPIONAGE. THIS INCLUDES, BUT IS NOT LIMITED TO,
#    CIVIL SERVICES RUN BY THE MILITARY, SUCH AS MILITARY HOSPITALS.
#
#
# ----- REQUIREMENTS ----- 
#
#    This program was developed under Python Version 2.7.6 for Windows 32bit
#    a windows standalone executable can be "compiled" with PyInstaller or py2exe
#
#
# ----- to do -----
#
#    see the comments "# some issue here: ....", basically the following:
#       - check reverse translation of Slice Orientation (should be OK)
#       - check reverse translation of anisotropy direction (probably doen't matter)
#   error conditions and messaging in case somke XML tag is not found
#   more general/better handling of the 3 "find_xml_" soubroutines
#   improove handling of array type XML tags ("Phase Encoding Velocity" and "Pixel Spacing")    
#


import xml.etree.ElementTree as ET
import sys, os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def find_xml_seriesinfo(name):
    result=''
    for info in root[0]:
        if info.get('Name')==(name):
            result=info.text
    return result
def find_xml_imageinfo1(name,index):
    result=''
    for info in root[1][index][0]:
        if info.get('Name')==(name):
            result=info.text
    return result
def find_xml_imageinfo2(name,index):
    result=''
    for info in root[1][index]:
        if info.get('Name')==(name):
            result=info.text
    return result    
    
def format_number(str_number,digits):
    form = "{:."+str(digits)+"f}"
    num = form.format(float(str_number))
    return str(num)    
def form_str_len (str,size):
    result=''
    if len(str)>=size-1: result=' '+str[0:size-1]
    else: 
        for i in range(0, size-len(str)): result+=' '
        result+=str
    return result
 
#  ------------------- Main programm starts here ---------------------------

TKwindows = Tk(); TKwindows.withdraw() #hiding tkinter window
TKwindows.attributes( '-topmost', True ) #stay on top
TKwindows.overrideredirect(True) # even over fullscreen apps


# open file dialog
input_file = askopenfilename(title="Open IVIM Diffusion file", filetypes=[("XML files",".xml"),("XML files", "*.XML")])
if input_file == "":
    print('No input file specified')
    sys.exit(1)


tree = ET.parse(input_file)
root = tree.getroot()

#open outfile
output_file = os.path.splitext(input_file)[0]+'.PAR'
outfile = open(output_file, 'w');

#write header
outfile.write ('# === DATA DESCRIPTION FILE ======================================================\n')
outfile.write ('#\n')
outfile.write ('# CAUTION - Investigational device.\n')
outfile.write ('# Limited by Federal Law to investigational use.\n')
outfile.write ('#\n')
outfile.write ('# Dataset name: '+input_file[:input_file.find('.')]+'\n')
outfile.write ('#\n')
outfile.write ('# CLINICAL TRYOUT             Research image export tool     V4.2\n')
outfile.write ('#\n')
outfile.write ('# === GENERAL INFORMATION ========================================================\n')
outfile.write ('#\n')

#write general info
outfile.write ('.    Patient name                       :   '+find_xml_seriesinfo ('Patient Name')+'\n')
outfile.write ('.    Examination name                   :   '+find_xml_seriesinfo ('Examination Name')+'\n')
outfile.write ('.    Protocol name                      :   '+find_xml_seriesinfo ('Protocol Name')+'\n')
outfile.write ('.    Examination date/time              :   '+find_xml_seriesinfo ('Examination Date')+' / '+find_xml_seriesinfo ('Examination Time')+'\n')
outfile.write ('.    Series Type                        :   Image   MRSeries\n')
outfile.write ('.    Acquisition nr                     :   '+find_xml_seriesinfo ('Aquisition Number')+'\n')
outfile.write ('.    Reconstruction nr                  :   '+find_xml_seriesinfo ('Reconstruction Number')+'\n')
outfile.write ('.    Scan Duration [sec]                :   '+format_number(find_xml_seriesinfo ('Scan Duration'),0)+'\n')
outfile.write ('.    Max. number of cardiac phases      :   '+find_xml_seriesinfo ('Max No Phases')+'\n')
outfile.write ('.    Max. number of echoes              :   '+find_xml_seriesinfo ('Max No Echoes')+'\n')
outfile.write ('.    Max. number of slices/locations    :   '+find_xml_seriesinfo ('Max No Slices')+'\n')
outfile.write ('.    Max. number of dynamics            :   '+find_xml_seriesinfo ('Max No Dynamics')+'\n')
outfile.write ('.    Max. number of mixes               :   '+find_xml_seriesinfo ('Max No Mixes')+'\n')
pos=find_xml_seriesinfo ('Patient Position')
position=''
if pos.find('HF')>=0: position += 'Head First'
if pos.find('FF')>=0: position += 'Feet First'
if pos.find('S')>=0: position += ' Supine'
if pos.find('P')>=0: position += ' Prone'
if pos.find('D')>=0: position += ' Decubitus'
if pos.find('R')>=0: position += ' Right'
if pos.find('L')>=0: position += ' Left'
if position=='': position=pos
outfile.write ('.    Patient position                   :   '+position+'\n')
prep=find_xml_seriesinfo ('Preparation Direction')
if prep.find('AP')>=0: prep= 'Anterior-Posterior'
elif prep.find('RL')>=0: prep= 'Right-Left'
elif prep.find('FH')>=0: prep= 'Foot-Head'
outfile.write ('.    Preparation direction              :   '+prep+'\n')
outfile.write ('.    Technique                          :   '+find_xml_seriesinfo ('Technique')+'\n')
outfile.write ('.    Scan resolution  (x, y)            :   '+find_xml_seriesinfo ('Scan Resolution X')+'  '+find_xml_seriesinfo ('Scan Resolution Y')+'\n')
outfile.write ('.    Scan mode                          :   '+find_xml_seriesinfo ('Scan Mode')+'\n')
tmpTR = find_xml_seriesinfo ('Repetition Times');
tmpTR1 = tmpTR[0]
# outfile.write ('.    Repetition time [ms]               :   '+format_number(find_xml_seriesinfo ('Repetition Times'),3)+'\n')
outfile.write ('.    Repetition time [ms]               :   '+format_number(tmpTR1,3)+'\n')
outfile.write ('.    FOV (ap,fh,rl) [mm]                :   '+format_number(find_xml_seriesinfo ('FOV AP'),3)+'  '+format_number(find_xml_seriesinfo ('FOV FH'),3)+'  '+format_number(find_xml_seriesinfo ('FOV RL'),3)+'\n')
outfile.write ('.    Water Fat shift [pixels]           :   '+format_number(find_xml_seriesinfo ('Water Fat Shift'),3)+'\n')
outfile.write ('.    Angulation midslice(ap,fh,rl)[degr]:   '+format_number(find_xml_seriesinfo ('Angulation AP'),3)+'  '+format_number(find_xml_seriesinfo ('Angulation FH'),3)+'  '+format_number(find_xml_seriesinfo ('Angulation RL'),3)+'\n')
outfile.write ('.    Off Centre midslice(ap,fh,rl) [mm] :   '+format_number(find_xml_seriesinfo ('Off Center AP'),3)+'  '+format_number(find_xml_seriesinfo ('Off Center FH'),3)+'  '+format_number(find_xml_seriesinfo ('Off Center RL'),3)+'\n')
flowcomp=find_xml_seriesinfo ('Flow Compensation')
if flowcomp=='N': flowcomp='0';
else: flowcomp='1'
outfile.write ('.    Flow compensation <0=no 1=yes> ?   :   '+flowcomp+'\n')
presat=find_xml_seriesinfo ('Presaturation')
if presat=='N': presat='0';
else: presat='1'
outfile.write ('.    Presaturation     <0=no 1=yes> ?   :   '+presat+'\n')
dummy=str(find_xml_seriesinfo ('Phase Encoding Velocity'))
str1=dummy.split()[0]
str2=dummy.split()[1]
str3=dummy.split()[2]
outfile.write ('.    Phase encoding velocity [cm/sec]   :   '+format_number(str1,6)+'  '+format_number(str2,6)+'  '+format_number(str3,6)+'\n')
mtc=find_xml_seriesinfo ('MTC')
if mtc=='N': mtc='0';
else: mtc='1'
outfile.write ('.    MTC               <0=no 1=yes> ?   :   '+mtc+'\n')
spir=find_xml_seriesinfo ('SPIR')
if spir=='N': spir='0';
else: spir='1'
outfile.write ('.    SPIR              <0=no 1=yes> ?   :   '+spir+'\n')
outfile.write ('.    EPI factor        <0,1=no EPI>     :   '+find_xml_seriesinfo ('EPI factor')+'\n')
dyn=find_xml_seriesinfo ('Dynamic Scan')
if dyn=='N': dyn='0';
else: dyn='1'
outfile.write ('.    Dynamic scan      <0=no 1=yes> ?   :   '+dyn+'\n')
diff=find_xml_seriesinfo ('Diffusion')
if diff=='N': diff='0';
else: diff='1'
outfile.write ('.    Diffusion         <0=no 1=yes> ?   :   '+diff+'\n')
outfile.write ('.    Diffusion echo time [ms]           :   '+format_number(find_xml_seriesinfo ('Diffusion Echo Time'),4)+'\n')
outfile.write ('.    Max. number of diffusion values    :   '+find_xml_seriesinfo ('Max No B Values')+'\n')
outfile.write ('.    Max. number of gradient orients    :   '+find_xml_seriesinfo ('Max No Gradient Orients')+'\n')
outfile.write ('.    Number of label types   <0=no ASL> :   '+find_xml_seriesinfo ('No Label Types')+'\n')

#write instructions
outfile.write ('#\n')
outfile.write ('# === PIXEL VALUES =============================================================\n')
outfile.write ('#  PV = pixel value in REC file, FP = floating point value, DV = displayed value on console\n')
outfile.write ('#  RS = rescale slope,           RI = rescale intercept,    SS = scale slope\n')
outfile.write ('#  DV = PV * RS + RI             FP = DV / (RS * SS)\n')
outfile.write ('#\n')
outfile.write ('# === IMAGE INFORMATION DEFINITION =============================================\n')
outfile.write ('#  The rest of this file contains ONE line per image, this line contains the following information:\n')
outfile.write ('#\n')
outfile.write ('#  slice number                             (integer)\n')
outfile.write ('#  echo number                              (integer)\n')
outfile.write ('#  dynamic scan number                      (integer)\n')
outfile.write ('#  cardiac phase number                     (integer)\n')
outfile.write ('#  image_type_mr                            (integer)\n')
outfile.write ('#  scanning sequence                        (integer)\n')
outfile.write ('#  index in REC file (in images)            (integer)\n')
outfile.write ('#  image pixel size (in bits)               (integer)\n')
outfile.write ('#  scan percentage                          (integer)\n')
outfile.write ('#  recon resolution (x y)                   (2*integer)\n')
outfile.write ('#  rescale intercept                        (float)\n')
outfile.write ('#  rescale slope                            (float)\n')
outfile.write ('#  scale slope                              (float)\n')
outfile.write ('#  window center                            (integer)\n')
outfile.write ('#  window width                             (integer)\n')
outfile.write ('#  image angulation (ap,fh,rl in degrees )  (3*float)\n')
outfile.write ('#  image offcentre (ap,fh,rl in mm )        (3*float)\n')
outfile.write ('#  slice thickness (in mm )                 (float)\n')
outfile.write ('#  slice gap (in mm )                       (float)\n')
outfile.write ('#  image_display_orientation                (integer)\n')
outfile.write ('#  slice orientation ( TRA/SAG/COR )        (integer)\n')
outfile.write ('#  fmri_status_indication                   (integer)\n')
outfile.write ('#  image_type_ed_es  (end diast/end syst)   (integer)\n')
outfile.write ('#  pixel spacing (x,y) (in mm)              (2*float)\n')
outfile.write ('#  echo_time                                (float)\n')
outfile.write ('#  dyn_scan_begin_time                      (float)\n')
outfile.write ('#  trigger_time                             (float)\n')
outfile.write ('#  diffusion_b_factor                       (float)\n')
outfile.write ('#  number of averages                       (integer)\n')
outfile.write ('#  image_flip_angle (in degrees)            (float)\n')
outfile.write ('#  cardiac frequency   (bpm)                (integer)\n')
outfile.write ('#  minimum RR-interval (in ms)              (integer)\n')
outfile.write ('#  maximum RR-interval (in ms)              (integer)\n')
outfile.write ('#  TURBO factor  <0=no turbo>               (integer)\n')
outfile.write ('#  Inversion delay (in ms)                  (float)\n')
outfile.write ('#  diffusion b value number    (imagekey!)  (integer)\n')
outfile.write ('#  gradient orientation number (imagekey!)  (integer)\n')
outfile.write ('#  contrast type                            (string)\n')
outfile.write ('#  diffusion anisotropy type                (string)\n')
outfile.write ('#  diffusion (ap, fh, rl)                   (3*float)\n')
outfile.write ('#  label type (ASL)            (imagekey!)  (integer)\n')
outfile.write ('#\n')
outfile.write ('# === IMAGE INFORMATION ==========================================================\n')
outfile.write ('#  sl ec  dyn ph ty    idx pix scan% rec size                (re)scale              window        angulation              offcentre        thick   gap   info      spacing     echo     dtime   ttime    diff  avg  flip    freq   RR-int  turbo delay b grad cont anis         diffusion       L.ty\n')
outfile.write ('\n')

#write frame data
End=False
index=0
while not End:
    outfile.write (form_str_len(find_xml_imageinfo1('Slice',index),4))
    outfile.write (form_str_len(find_xml_imageinfo1('Echo',index),4))
    outfile.write (form_str_len(find_xml_imageinfo1('Dynamic',index),5))
    outfile.write (form_str_len(find_xml_imageinfo1('Phase',index),3))
    type=find_xml_imageinfo1('Type',index)
    imagetypes = ['M','R','I','P','CR','T0','T1','T2', 'RHO','SPECTRO','DERIVED','ADC','RCBV','RCBF','MTT','TTP','FA','EADC','B0','DELAY','MAXRELENH','RELENH','MAXENH','WASHIN','WASHOUT','BREVENH','AREACURV','ANATOMIC','T_TEST','STD_DEVIATION','PERFUSION','T2_STAR','R2','R2_STAR','W','IP','OP','F','SPARE1','SPARE2']
    try: type=str(imagetypes.index(type))
    except: type='0'
    outfile.write (' '+type)
    seq=find_xml_imageinfo1('Sequence',index)
    sequences = ['IR','SE','FFE','DERIVED','PCA','UNSPECIFIED','SPECTRO','SI']
    try: seq=str(sequences.index(seq))
    except: sequence='5'
    outfile.write (form_str_len(seq,2))
    outfile.write (form_str_len(find_xml_imageinfo1('Index',index),6))
    outfile.write (form_str_len(find_xml_imageinfo2('Pixel Size',index),4))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Scan Percentage',index),0),6))
    outfile.write (form_str_len(find_xml_imageinfo2('Resolution X',index),5))
    outfile.write (form_str_len(find_xml_imageinfo2('Resolution Y',index),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Rescale Intercept',index),5),12))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Rescale Slope',index),5),10))
    outfile.write (form_str_len(find_xml_imageinfo2('Scale Slope',index).replace("E","e"),13))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Window Center',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Window Width',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation AP',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation FH',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation RL',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter AP',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter FH',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter RL',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Slice Thickness',index),3),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Slice Gap',index),3),7))
    disp_orient = find_xml_imageinfo2('Display Orientation',index)
    disp_orientations= ['NONE','RIGHT90','RIGHT180','LEFT90','VM','RIGHT90VM','RIGHT180VM','LEFT90VM']
    try: disp_orient=str(disp_orientations.index(disp_orient))
    except: disp_orient='0'
    outfile.write (form_str_len(disp_orient,2))
    sl_orient = find_xml_imageinfo2('Slice Orientation',index)
    sl_orient = sl_orient.lower()
    if sl_orient.find('tra')>=0: sl_orient='1'   # some issue here: what are the other possibilities
    elif sl_orient.find('sag')>=0: sl_orient='2' # some issue here: is that correct?
    elif sl_orient.find('cor')>=0: sl_orient='3' # some issue here: is that correct?
    else: sl_orient='0'
    outfile.write (form_str_len(sl_orient,2))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('fMRI Status Indication',index),0),2))
    type_ed_es = find_xml_imageinfo2('Image Type Ed Es',index)
    if type_ed_es.find('U')>=0: type_ed_es='2'
    elif type_ed_es.find('ED')>=0: type_ed_es='0'
    elif type_ed_es.find('ES')>=0: type_ed_es='1'
    else: type_ed_es='2'
    outfile.write (form_str_len(type_ed_es,2))
    dummy=str(find_xml_imageinfo2('Pixel Spacing',index))
    str1=dummy.split()[0]
    str2=dummy.split()[1]
    outfile.write (form_str_len(format_number(str1,3),7))
    outfile.write (form_str_len(format_number(str2,3),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Echo Time',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Dyn Scan Begin Time',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Trigger Time',index),2),9))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion B Factor',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('No Averages',index),0),4))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Image Flip Angle',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Cardiac Frequency',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Min RR Interval',index),0),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Max RR Interval',index),0),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('TURBO Factor',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Inversion Delay',index),1),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo1('BValue',index),0),3))
    outfile.write (form_str_len(format_number(find_xml_imageinfo1('Grad Orient',index),0),4))
    contr=find_xml_imageinfo2('Contrast Type',index)
    contrasttypes = ['DIFFUSION','FLOW_ENCODED','FLUID_ATTENUATED','PERFUSION','PROTON_DENSITY','STIR','TAGGING','T1','T2','T2_STAR','TOF','UNKNOWN','MIXED']
    try: contr=str(contrasttypes.index(contr))
    except: contr='11'
    outfile.write (form_str_len(contr,5))
    anis=find_xml_imageinfo2('Diffusion Anisotropy Type',index)
    if anis=='-': anis='0' # some issue here: what are the other possibilities
    outfile.write (form_str_len(anis,5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion AP',index),3),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion FH',index),3),9))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion RL',index),3),9))
    labletype=find_xml_imageinfo1('Label Type',index)
    if labletype=='-': labletype='1'
    elif labletype.find('L')>=0: labletype='1'
    elif labletype.find('l')>=0: labletype='1'
    else: labletype='0'
    outfile.write (form_str_len(labletype,3))
    outfile.write ('\n')
    index+=1
    try: test = find_xml_imageinfo1('Slice',index)
    except: End=True


outfile.write ('\n')
outfile.write ('# === END OF DATA DESCRIPTION FILE ===============================================\n')
outfile.close()

