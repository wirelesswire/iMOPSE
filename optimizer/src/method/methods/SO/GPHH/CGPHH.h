#pragma once

#include "../../../operators/initialization/AInitialization.h"
#include "../../../operators/crossover/ACrossover.h"
#include "../../../operators/mutation/AMutation.h"
#include "../../../individual/SO/SSOIndividual.h"
#include "../../../configMap/SConfigMap.h"
#include "../../../operators/selection/selections/CFitnessTournament.h"
#include "../../../AGeneticMethod.h"
#include "../ASOGeneticMethod.h"

class CGPHH : public ASOGeneticMethod
{
public:
    CGPHH(
            std::vector<float> &objectiveWeights,
            AProblem &evaluator,
            AInitialization &initialization,
            CFitnessTournament &fitnessTournament,
            ACrossover &crossover,
            AMutation &mutation,
            SConfigMap *configMap
    );
    ~CGPHH() override = default;

    void RunOptimization() override;
private:
    CFitnessTournament &m_FitnessTournament;

    void CreateIndividual();
    void EvolveToNextGeneration();
};