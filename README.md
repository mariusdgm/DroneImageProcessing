# DroneImageProcessing

This repository contains the codebase for the National Instruments Student challenge 2017, where this project won the 3rd place. 

## Project description

The project proposes the use of drones to perform visual inspection of difficult to reach structures. 

The vi. files contain the labview code used to control a Parrot drone and aquire the images from the front mounted camera.

An image classifier then scans the images and outputs the predominant defect that was observed. The classifier used is an Inception model that was retrained with the classes of interest in this use case: cracks, rust, graffiti and normal.