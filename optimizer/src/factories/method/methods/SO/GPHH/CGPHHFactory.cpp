
#include <stdexcept>
#include "CGPHHFactory.h"
#include "../../../../../utils/fileReader/CReadUtils.h"
#include "../../../operators/selection/CSelectionFactory.h"

std::vector<float> *CGPHHFactory::objectiveWeights = nullptr;
CFitnessTournament *CGPHHFactory::fitnessTournament = nullptr;

CGPHH *CGPHHFactory::CreateGPHH(SConfigMap *configMap, AProblem &problem, AInitialization *initialization,
                          ACrossover *crossover,
                          AMutation *mutation)
{
    objectiveWeights = new std::vector<float>();
    std::string rawWeightsString;
    configMap->TakeValue("ObjectiveWeights", rawWeightsString);

    if (!rawWeightsString.empty())
    {
        CReadUtils::ReadWeights(rawWeightsString, *objectiveWeights);
    } else {
        *objectiveWeights = {1.0f};
    }
    
    fitnessTournament = CSelectionFactory::CreateFitnessTournamentSelection(configMap);

    return new CGPHH(
            *objectiveWeights,
            problem,
            *initialization,
            *fitnessTournament,
            *crossover,
            *mutation,
            configMap
    );
}

void CGPHHFactory::DeleteObjects()
{
    delete objectiveWeights;
    delete fitnessTournament;
}
