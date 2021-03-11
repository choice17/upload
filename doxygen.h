/**
 * @file doxygen.h
 * @brief doxygen example header
 */

#include <stdio.h>

#include "common.h"

/**
 * @brief Struct of rectangle.
 * Details: Store start and end points.
 */
typedef struct {
    int sx; /**< start x. */
    int sy; /**< start y. */
} rectangle;

/**
 * @brief save rectangle
 * Details: Save something.
 * @see LoadRect()
 * @param[in] rect rectangle
 * @return The execution result
 *  0 - success
 *  1 - failure
 */
int SaveRect(const rectangle *rect);

/**
 * @brief load rect
 * @see SaveRect()
 * @param[out] rect rectangle
 * @return The execution result
 *  0 - success
 *  1 - failure
 */
int LoadRect(rectangle *rect);
