/* reference https://www.geeksforgeeks.org/merge-sort/ */

/* C program for Merge Sort */
#include <stdlib.h> 
#include <stdio.h> 
#include <string.h>

// Merges two subarrays of arr[]. 
// First subarray is arr[l..m] 
// Second subarray is arr[m+1..r]
void merge(int arr[], int l, int m, int r) 
{ 
    int i, j, k; 
    int n1 = m - l + 1; 
    int n2 =  r - m; 
  
    /* create temp arrays */
    int L[n1], R[n2]; 
  
    /* Copy data to temp arrays L[] and R[] */
    for (i = 0; i < n1; i++) 
        L[i] = arr[l + i]; 
    for (j = 0; j < n2; j++) 
        R[j] = arr[m + 1+ j]; 
  
    /* Merge the temp arrays back into arr[l..r]*/
    i = 0; // Initial index of first subarray 
    j = 0; // Initial index of second subarray 
    k = l; // Initial index of merged subarray 
    while (i < n1 && j < n2) { 
        if (L[i] <= R[j]) { 
            arr[k] = L[i]; 
            i++; 
        } else { 
            arr[k] = R[j]; 
            j++; 
        } 
        k++; 
    } 
  
    /* Copy the remaining elements of L[], if there 
       are any */
    while (i < n1) { 
        arr[k] = L[i]; 
        i++; 
        k++; 
    } 
  
    /* Copy the remaining elements of R[], if there 
       are any */
    while (j < n2) { 
        arr[k] = R[j]; 
        j++; 
        k++; 
    } 
} 
  
/* l is for left index and r is right index of the 
   sub-array of arr to be sorted */
void mergeSort(int arr[], int l, int r) 
{ 
    if (l < r) { 
        // Same as (l+r)/2, but avoids overflow for 
        // large l and h 
        int m = l+(r-l)/2; 
  
        // Sort first and second halves 
        mergeSort(arr, l, m); 
        mergeSort(arr, m+1, r); 
  
        merge(arr, l, m, r); 
    } 
} 


// Merges two subarrays of arr[]. 
// First subarray is arr[l..m] 
// Second subarray is arr[m+1..r]
void mergeGeneral(void *arr, int l, int m, int r, size_t sz, int (*compare_func)(const void *, const void *)) 
{ 
    int i, j, k; 
    int n1 = m - l + 1; 
    int n2 =  r - m; 
  
    /* create temp arrays */
    unsigned char L[n1 * sz], R[n2 * sz]; 
  
    /* Copy data to temp arrays L[] and R[] */
    for (i = 0; i < n1; i++) 
        memcpy(&L[i * sz], (unsigned char *)(arr + (l + i) * sz), sz); 
    for (j = 0; j < n2; j++)
        memcpy(&R[j * sz], (unsigned char *)(arr + (m + 1+ j) * sz), sz);
  
    /* Merge the temp arrays back into arr[l..r]*/
    i = 0; // Initial index of first subarray 
    j = 0; // Initial index of second subarray 
    k = l; // Initial index of merged subarray 
    while (i < n1 && j < n2) {
        if (compare_func((const void *)(L + i*sz), (const void *)(R + j*sz))) {
            memcpy((unsigned char*)(arr + k * sz), (unsigned char*)(L + i * sz), sz); 
            //arr[k] = L[i]; 
            i++; 
        } else {
            memcpy((unsigned char*)(arr + k * sz), (unsigned char*)(R + j * sz), sz); 
            //arr[k] = R[j]; 
            j++; 
        } 
        k++; 
    } 
  
    /* Copy the remaining elements of L[], if there 
       are any */
    while (i < n1) {
        memcpy((unsigned char*)(arr + k * sz), (unsigned char*)(L + i * sz), sz); 
        //arr[k] = L[i]; 
        i++; 
        k++; 
    } 
  
    /* Copy the remaining elements of R[], if there 
       are any */
    while (j < n2) {
        memcpy((unsigned char*)(arr + k * sz), (unsigned char*)(R + j * sz), sz); 
        //arr[k] = R[j]; 
        j++; 
        k++; 
    } 
} 

/* l is for left index and r is right index of the 
   sub-array of arr to be sorted */
void mergeSortGeneral(void *arr, int l, int r, size_t sz, int (*compare_func)(const void *, const void *)) 
{ 
    if (l < r) { 
        // Same as (l+r)/2, but avoids overflow for 
        // large l and h 
        int m = l+(r-l)/2; 
  
        // Sort first and second halves 
        mergeSortGeneral(arr, l, m, sz, compare_func); 
        mergeSortGeneral(arr, m+1, r, sz, compare_func); 
  
        mergeGeneral(arr, l, m, r, sz, compare_func); 
    } 
} 

/* UTILITY FUNCTIONS */
/* Function to print an array */
void printArray(void *A, int size, size_t sz, int (*return_method)(const void *)) 
{ 
    int i;
    for (i=0; i < size; i++) 
        printf("%d ", (return_method)((const void *)(A + i * sz))); 
    printf("\n"); 
} 

typedef struct {
    int val;
    int dummy0;
    int dummy1;
    int dummy2;
} VAL_S;

int compare_func(const void *ld, const void *rd)
{
    VAL_S *l = (VAL_S *)ld;
    VAL_S *r = (VAL_S *)rd;
    return (l->val) > (r->val) ? 0 : 1; 
}

int compare_func_desc(const void *ld, const void *rd)
{
    VAL_S *l = (VAL_S *)ld;
    VAL_S *r = (VAL_S *)rd;
    return (l->val) > (r->val) ? 1 : 0; 
}


int return_int(const void *data)
{
    return *(int *)data;
}

int return_var(const void *data)
{
    return ((VAL_S *)data)->val;
}

/* Driver program to test above functions */
int main() 
{ 
    int arr[] = {12, 11, 13, 5, 6, 7}; 
    int arr_size = sizeof(arr)/sizeof(arr[0]); 
  
    printf("Given array is \n"); 
    printArray((void *)arr, arr_size, sizeof(int), return_int); 
  
    mergeSort(arr, 0, arr_size - 1); 

    printf("\nSorted array is \n"); 
    printArray((void *)arr, arr_size, sizeof(int), return_int); 

#define ARR_SIZE (6)

    VAL_S varr[ARR_SIZE] = {{12,0},{11,0},{13,0},{5,0},{6,0},{7,0}};
    printf("\nGiven varray is \n");
    printArray(varr, arr_size, sizeof(VAL_S), return_var); 

    mergeSortGeneral(varr, 0, ARR_SIZE - 1, sizeof(VAL_S), compare_func);

    printf("\nSorted asce array is \n");
    printArray(varr, arr_size, sizeof(VAL_S), return_var); 

    VAL_S _varr[ARR_SIZE] = {{12,0},{11,0},{13,0},{5,0},{6,0},{7,0}};
    mergeSortGeneral(_varr, 0, ARR_SIZE - 1, sizeof(VAL_S), compare_func_desc);

    printf("\nSorted desc array is \n");
    printArray(_varr, arr_size, sizeof(VAL_S), return_var); 
    return 0; 
} 
