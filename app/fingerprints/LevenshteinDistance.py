def LowerOfThree(num1,num2,num3):
    if num1<=num2:
        tmp=num1
    else:
        tmp=num2
    if tmp<=num3:
        return tmp
    else:
        return num3

def LevenshteinDistance(str1,str2):
    matrix=[]
    m=len(str1)
    n=len(str2)
    for x in range(m+1):
        tmp=[]
        for i in range(n+1):
            tmp.append(0)
        matrix.append(list(tmp))

    for i in range(n+1):
        matrix[0][i]=i
    for i in range(m+1):
        matrix[i][0]=i

    for nn in range(1,n+1):
        char=str2[nn-1]
        for mm in range(1,m+1):
            if char==str1[mm-1]:
                matrix[mm][nn]=LowerOfThree(matrix[mm][nn-1]+1,matrix[mm-1][nn]+1,matrix[mm-1][nn-1])
            else:
                matrix[mm][nn]=LowerOfThree(matrix[mm][nn-1]+1,matrix[mm-1][nn]+1,matrix[mm-1][nn-1]+1)

    return matrix[m][n]

if __name__=="__main__":
    str2="jerry"
    str1="jary"
    print(LevenshteinDistance(str1,str2))
