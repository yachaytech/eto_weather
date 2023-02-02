The eto_weather project classifies water evaporation for a particular area by using the variables needed to calculate standard evaporation, ETo, as given by the Food and Agriculture Organization.

The approach is to use a self-organizing AI neural network map (SOM) over a region to cluster areas (pixels) with similar weather components. These variables are derived from the Weather, Reasearch and Forecast (WRF) numerical prediction model, which you will need to install or have access to the daily output. Helpful scripts to automate WRF runs can be found in the "WRFscripts" project.

For this project, we used a spatial resolution of ~3x3 kilometers per pixel, with a region of 171x171 pixels over the Ecuadorian Andes and Amazon. Twenty-five weather classes were rendered. 

Because of the random/stochastic nature of SOM, much attention was given to repeatabilty for a series of runs. Here we used a version of Cramer-V similarity version. 

(work in progress, more to come)