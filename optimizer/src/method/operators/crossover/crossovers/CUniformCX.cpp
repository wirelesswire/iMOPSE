#include "CUniformCX.h"
#include "../../../../utils/random/CRandom.h"


/// <summary>
/// this class implements uniform crossover operator.
/// </summary>
/// <param name="problemEncoding"></param>
/// <param name="firstParent"></param>
/// <param name="secondParent"></param>
/// <param name="firstChild"></param>
/// <param name="secondChild"></param>
void CUniformCX::Crossover(const SProblemEncoding& problemEncoding, AIndividual &firstParent, AIndividual &secondParent,
                           AIndividual &firstChild,
                           AIndividual &secondChild)
{
    const size_t sectionSize = problemEncoding.m_Encoding[0].m_SectionDescription.size();
    if (CRandom::GetFloat(0.0f, 1.0f) < m_CrossoverProbability)
    {
        for (size_t g = 0; g < sectionSize; ++g)
        {
            if (CRandom::GetFloat(0.0f, 1.0f) < 0.5f)
            {
                firstChild.m_Genotype.m_FloatGenotype[g] = secondParent.m_Genotype.m_FloatGenotype[g];
            }
            // Check explicitly both sides ??
            if (CRandom::GetFloat(0.0f, 1.0f) < 0.5f)
            {
                secondChild.m_Genotype.m_FloatGenotype[g] = firstParent.m_Genotype.m_FloatGenotype[g];
            }
        }
    }
}
