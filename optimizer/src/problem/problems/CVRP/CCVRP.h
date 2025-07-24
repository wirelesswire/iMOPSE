#pragma once

#include "CCVRPTemplate.h"
#include "../../AProblem.h"
#include "../../../method/individual/SGenotype.h"


/// <summary>
/// implements the Cumulative Capacitated Vehicle Routing Problem (CCVRP)
/// </summary>
class CCVRP : public AProblem {
public:
    explicit CCVRP(CCVRPTemplate& cvrpBase);

    ~CCVRP() override = default;

    
    
    SProblemEncoding& GetProblemEncoding() override;

    //TODO czmu to jest void ? 
    void Evaluate(AIndividual& individual) override;
    
    
    void LogSolution(AIndividual& individual) override;
    void LogAdditionalData() override {};


protected:
    
    
    size_t GetNearestDepotIdx(size_t cityIdx);
    /// <summary>
	/// m_UpperBounds contains the upper bounds for each objective function.
	/// m_ProblemEncoding contains the problem encoding for the CCVRP.
	/// m_CVRTemplate is a reference to the CCVRPTemplate object that holds the problem data.
	/// m_MaxObjectiveValues contains the maximum values for each objective function. /// czyli to chyba nie dla mnie 
	/// m_MinObjectiveValues contains the minimum values for each objective function.
    /// </summary>
    std::vector<size_t> m_UpperBounds;
    SProblemEncoding m_ProblemEncoding;
    CCVRPTemplate& m_CVRPTemplate;
    std::vector<float> m_MaxObjectiveValues;
    std::vector<float> m_MinObjectiveValues;

private:
    void CreateProblemEncoding();
};
