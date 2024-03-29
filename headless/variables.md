[]{#anchor}

+--------------------------+---------------+------------------------------------------------------------------------------------+
| Variable                 | Default Value | Description                                                                        |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| People                   | 50            | Initial number of people in the forager band                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| MaximumPeople            | 3000          | Maximum human population                                                           |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| HumanBirthRate           | 0.032         | Human birth rate (per annum)                                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| HumanDeathRate           | 0.03          | Human death rate (per annum)                                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| HumanBirthDeathFilter    | 0.005         | Width of the Gaussian randomizing filter for human birth and death rates           |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| StarvationThreshold      | 0.8           | Human starvation threshold (percentage of per annum kcal need)                     |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| HumanKcal                | 912500        | Yearly per capita kcal need                                                        |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| ForagingHours            | 4380          | Per capita hours of work available per annum                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| ForagingUncertainty      | 0.1           | Width of the Gaussian randomizing filter for foraging returns                      |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| Prey                     | 200           | Initial number of prey                                                             |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| MaxPrey                  | 500           | Maximum number of prey                                                             |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyMigrants             | 0             | Number of prey that migrate into the territory per annum                           |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyBirthRate            | 0.06          | Prey birth rate                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyDeathRate            | 0.04          | Intrinsic prey death rate (without human hunting)                                  |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyBirthDeathFilter     | 0.005         | Width of the Gaussian randomizing filter for prey birth and death rates            |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyReturns              | 200000        | Kcal return from an average prey                                                   |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreySearchCost           | 72.0          | Hours search time to find a prey                                                   |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyDensity              | 1000          | Density for which the search time is known                                         |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| MaxPreyEncountered       | 4             | Maximum number of prey per encounter                                               |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| MinPreyEncountered       | 1             | Minimum number of prey per encounter                                               |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| PreyHandlingCost         | 16            | Hours of handling time per encounter                                               |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| Cereal                   | 100           | Number of cereal patches (assume 1ha/patch)                                        |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| WildCerealReturns        | 0.05          | Return rate (kcal) per wild-type cereal seed                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| DomesticatedCereal       | 0.1           | Return rate (kcal) per domestic-type cereal seed                                   |
|                          |               |                                                                                    |
| Returns                  |               |                                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| WildToDomesticated       | 0.98          | Initial proportion of wild to domestic types                                       |
|                          |               |                                                                                    |
| Proportion               |               |                                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| CerealSelectionRate      | 0.03          | Selection coefficient (percentage per annum)                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| CerealDiffusionRate      | 0.02          | Diffusion coefficient (percentage per annum)                                       |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| SelectionDiffusionFilter | 0.001         | Width of the Gaussian filter applied to selection and diffusion rate               |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| CerealSearchCosts        | 1.0           | Hours of search time to find a cereal patch                                        |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| CerealDensity            | 10000000      | Initial (and minimum) number of individuals per patch                              |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| MaxCerealDensity         | 100000000     | Maximum number of individuals per patch, after human influence                     |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| CerealCultivation        | 1000000       | Rate at which cultivation increases the number of individuals in a patch per annum |
|                          |               |                                                                                    |
| Density                  |               |                                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| WildCerealHandling       | 0.0001        | Handling time (hours) per wild cereal seed                                         |
|                          |               |                                                                                    |
| Cost                     |               |                                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| DomesticatedCereal       | 0.00001       | Handling time (hours) per domestic cereal seed                                     |
|                          |               |                                                                                    |
| HandlingCost             |               |                                                                                    |
+--------------------------+---------------+------------------------------------------------------------------------------------+
| Years                    | 3000          | The number of years for which to run the simulation                                |
+--------------------------+---------------+------------------------------------------------------------------------------------+
