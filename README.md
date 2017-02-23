# wp03-landcover-framework
MELODIES Land Cover framework

This Work Package's objectives are:

• Develop methodologies for using EO to develop products useful for improving the calculation of emission
inventories

• Demonstrate how EO can provide a step-change for calculating land-use change emissions and
climate/wetness-dependent GHG emissions, compared with conventional data-gathering methods

• Present these products alongside other linked open data in an intuitive environment for researchers and
policymakers to use for analysis and decision making.


This repository contains the implementation of WP3.

--> GetData/, LandCover/ and MODIS/ contain the prototype code, written in a mixture of bash and python with several
undocumented dependencies, hard-coded paths and file names, obsolete code and files, and limited documentation.
However, it seems to work; there are no test suites available to confirm this though.

--> Operation python contains a production quality version of the code to download MODIS data and to process it
in gdal. A default configuration file is provided which controls the exact behaviour of each part. Start with

    "Operational python/GetData/src/getData.py"
    
to download files from the LPDAAC website, then use

    "Operational python/ProcessMOD/src/processMODISdata.py"
    
to do image processing.

Each module contains a test suite which may assist in understanding the code, and which MUST be run in the event
of any code changes. All classes are documented and "Operational python/EA_model_design" contains a selection of
design details comprising class and sequence diagrams. The majority of this code has been tested, the exception
being the more complex mathematical image manipulations. It has not been peer reviewed.



--------------------------------------------------------------------------------------------------------------------
Details of WP3 from DOW_MELODIES_603525_2015-05-28.pdf (available from EMDESK in Consortium docs folder)

Overview schedule:

First cycle: Scientific development of datasets required by the service (land cover, soil wetness etc – see tasks
below for details). Develop service storyboard in close consultation with users and WP2.

Second cycle: Implementation of service using first version of datasets. Evaluation of datasets and service in
conjunction with users. Scientific development of second version of datasets

Third cycle: Revision of service using first version of datasets. Evaluation of second version of datasets and
service in conjunction with users.

Task 3.1: Scientific and Technical coordination

This task encompasses activities connected with the coordination of developments across the project. This
will include preparation for, and attendance at, monthly Project Board meetings, and the preparation of key
deliverables that ensure effective and accurate communication of scientific and technical progress throughout
the project. The first such deliverable is a detailed description of the technical and data requirements of this
service (D3.1, month 3). This will inform the first iteration of the detailed Project Plan (delivered by WP2 at month
5). The remaining three deliverables are critical evaluations of the progress achieved in each of the project’s
three development cycles, together with feedback received from the Project Advisory Board and other users.
These will be used by WP2 to issue updates to the Project Plan in the second and third cycles.

WP 3.2 High temporal resolution Land Cover maps for GHG emissions

In the inventory of UK Land Use, Land Cover Change and Forestry (LULUCF), current knowledge on regional
crop rotation patterns and land-use changes is based on survey data (7-10 years apart) and expert judgment.
Areas of land-use change are the biggest source of uncertainty in the LULUCF inventory. In this work package
we will produce annual estimates of land cover and land cover change at a 1km scale using satellite data. The
techniques we employ will be carefully calibrated against high accuracy, reference UK data sets produced for
2000 and 2007 (LCM 2000, 2007 ).

Specific tasks will include:

• Derive land cover information from appropriate EO missions, using algorithms trained on LCM2000. A number
of state of the art techniques, such as Support Vector Machines, will be investigated.

• Use the LCM2007 data set to assess the performance of each technique and select the one to be used to
produce the outputs from the work package.

WT3:

Work package description

603525 MELODIES - Workplan table - Page 16 of 60

• Quantify the uncertainty from previous attempts at estimating land use change with EO by using high-resolution
data collected by the devolved administrations of the UK Government as ground truth. Some of these datasets
data will need to remain confidential, but the satellite product and its uncertainties can be made public.

• Spatialise the uncertainty estimates using existing techniques developed and published by members of the
team to provide the information on a scale relevant to the inventories.

WP 3.3 Uncertainties in agro-climatic zones from soil moisture variability

The wetness of the soil is a key climatic variable for GHG emissions from soils, in particular nitrous oxide
(N2O). Current efforts towards implementing a Tier 3 methodology for estimating UK N2O emissions are based
on dividing the country into different soil climatic zones, using a combination of soil type and wetness over
decadal climatologies. In this work package we will estimate the uncertainties in this ‘average’ climatology using
information on the month-to-month variability of soil moisture in the UK.

Specific tasks will include:

• Derive estimates of the variability in soil moisture over the UK using relevant products from ESA’s Climate
Change Initiative (observation-based) and model-based spatial datasets (e.g., CHESS/JULES, grid2grid);

• Compile database of freely-available historic soil moisture measurements made in the UK, and make available
as linked open data;

• Compare the available in situ measurements of soil moisture with the larger-scale soil moisture products,
together with the land cover information derived in WP3.1;

• Estimate the contribution of year-to-year or month-to-month variability of soil moisture in the UK to the
agroclimatic zones used for emissions inventory calculations and communicate with inventory compilers.

WP 3.4 Service development

This task includes all activity related to the development of a portal for accessing and exploring the data derived
in WP3.2 and 3.3. As the service development in this WP is starting from scratch and depends on some
research effort before it can be implemented, we do not intend to produce a deployable service for the first
development cycle. Instead, we will produce storyboards for presentation at the first meeting of the Project
Advisory Board to gather user feedback, and then proceed with implementing a real system in the second and
third cycles.

Specific tasks include:

• Produce a design (the service implementation storyboard) for the portal through liaison with users at, in
particular, Rothamsted Research, CEH, Defra and DECC;

• Work with the developers of the technology platform in WP2 to deliver such a portal;

• Work with informatics experts at CEH to host the datasets long-term and assess the feasibility of hosting
exploration tools through CEH’s publically accessible and INSPIRE-compliant Information Gateway;

• Work with the WP11 (Sustainability) to assess the feasibility of extending the datasets to the whole of the EU in
the future, based on the availability of appropriate driving data and validation data.

Data used in service:

EO: MERIS, MODIS, SPOT-VGT, Landsat, ESA soil moisture CCI products, GMES Geoland2; Meteorological
reanalyses; UK Land Cover map 2000, 2007; model-based spatial datasets (e.g., CHESS/JULES, grid2grid); in
situ soil moisture measurements; agricultural and activity data from data.gov.uk.
