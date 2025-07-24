#pragma once

#include <cstddef>
#include <vector>

struct SEncodingDescriptor
{
    float m_MinValue;
    float m_MaxValue;
};

/// <summary>
/// encoding types for the problem encoding
/// they are used to define how the problem is represented in the encoding sections
/// each type corresponds to a different way of encoding the problem's variables
 //association: used for encoding associations between variables, such as in a bipartite graph for example 
/// permutation: used for encoding permutations of variables, such as in a traveling salesman problem
/// binary: used for encoding binary variables, such as in a knapsack problem
/// 
/// </summary>

enum class EEncodingType
{
    ASSOCIATION = 0,
    PERMUTATION,
    BINARY,
};

/// <summary>
/// 
/// </summary>
struct SEncodingSection
{
    std::vector<SEncodingDescriptor> m_SectionDescription;
    EEncodingType m_SectionType;
};
/// <summary>
/// for my purpose only one is needed 
/// </summary>
struct SProblemEncoding
{
    int m_objectivesNumber;
    std::vector<SEncodingSection> m_Encoding;
    std::vector<std::vector<float>> m_additionalProblemData;
};