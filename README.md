# Advanced Electronic Devices - finFET and NSFET

This git repo contains Sentaurus design files for the AED coursework.
A baseline design was provided by the instructor. Two main branches were created from the baseline- A rounded top fin finFET, and a nanosheetFET.

This repo has four folders. One folder is dedicated to the sdevice commands which are common for all the designs. Simulations were performed to extract two transfer characteristic plots, one for the linear region and another for saturation; and three output characteristic curves. The value of Vd in the former case and Vg in the latter case can be tuned as required. The value of the workfunction is set to 4.6V for TiN, and can be configured as required.

There are more folders - Baseline, NanosheetFET and Rounded_FinFET. The Baseline folder contains the baseline sde command file provided in the tutorial. This command file was changes to have a rounded fin on the top of the channel and is stored in the Rounded_FinFET folder by the name - rounded_Poly. Next, the gate was changed to a metal - Titanium Nitride and the gate was also curved, to mimic an actual process node. The sde command file for this transistor was saved in rounded_TiN. This device was enhanced to have a taller fin and a thinner gate oxide, this is stored in rounded_TiN_enhanced.

The structure was changed to include nanosheets for making Gate All Around transistors. Three nanosheets were placed in the fin. The oxide material was chosen to be HfO2 and Si3N2 spacers were put in place to support the structure. A first version is stored in nanosheet_sde. Finally, the edges of the nanosheet and the top of the fin were rounded to mimic a real process node.

Performance parameter extraction was done using a python script stored in Xtracting_Performance_Parameters/ParameterExtraction_v5.py. The current file is for the curved edge NSFET. The data should be of a specific format, as put in the comments of the code.

Notes:
While rounding the edges, the analytical doping cross-section was not changed. This would not have a huge impact on the results as the protruding corners try to dope oxide, which does not carry current. An attempt to round the doping cross-section were made and have been put as comments in the rounded_TiN file.
