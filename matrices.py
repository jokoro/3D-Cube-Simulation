INVALID_MATRIX_MESSAGE = 'Matrix is empty, doesn\'t have same number of entries in ' \
                         'each column, and/or has at least 1 non-number entry.'
INVALID_MATRIX_MULT_MESSAGE = 'left_matrix number of columns != right_matrix number of rows'
NOT_SCALAR_MESSAGE = 'scalar is not a real number'
NOT_SAME_SIZE_MESSAGE = 'matrices are different sizes'


class InvalidMatrixError(Exception)
    pass


class InvalidCalcError(Exception):
    pass


class Matrix:
    def __init__(self, matrix: [[int or float]]) -> None:
        if valid_matrix(matrix):
            self.matrix = matrix
            self.rows = len(matrix)
            self.cols = len(matrix[0])
        else:
            raise InvalidMatrixError(INVALID_MATRIX_MESSAGE)


def valid_matrix(matrix: [[int or float]]) -> bool:
    """
    Returns True if matrix is non empty, organized in 2D list,
    has same number of entries in each column, and if all
    entries are actually numbers, but False otherwise.
    """
    if type(matrix) != list or len(matrix) == 0 or \
            type(matrix[0]) != list or len(matrix[0]) == 0:  # empty or not 2D list
        return False

    col_num = len(matrix[0])
    for row in matrix:
        if type(row) != list and col_num != len(row):  # not 2D list or not same number of entries in each column
            return False
        for col in row:
            if type(col) not in [int, float]:  # not all entries are numbers
                return False
    return True


def same_size_matrices(left_matrix: Matrix, right_matrix: Matrix) -> bool:
    """ Returns True if left_matrix size = right_matrix size. False otherwise. """
    return left_matrix.rows == right_matrix.rows and left_matrix.cols == right_matrix.cols


def valid_matrix_multiplication(left_matrix: Matrix, right_matrix: Matrix) -> bool:
    """ Returns True if left_matrix number of columns = right_matrix number of rows. False otherwise. """
    return left_matrix.cols == right_matrix.rows


def is_scalar(scalar: int or float) -> bool:
    """ Return True if scalar is a real number, False otherwise. """
    try:
        int(scalar)
        return True
    except ValueError:
        return False


def addition(left_matrix: Matrix, right_matrix: Matrix) -> Matrix:
    """ Returns a new matrix derived from adding left_matrix to right_matrix, provided they're compatible. """
    if same_size_matrices(left_matrix, right_matrix):
        new_matrix = []
        for i in range(left_matrix.rows):
            row = []
            for j in range(left_matrix.cols):
                row += [left_matrix.matrix[i][j] + left_matrix.matrix[i][j]]
            new_matrix += [row]
        return Matrix(new_matrix)
    else:
        raise InvalidCalcError(NOT_SAME_SIZE_MESSAGE)


def scalar_multiplication(matrix: Matrix, scalar: int or float) -> Matrix:
    """ Returns a new matrix derived from multiplying matrix by a scalar, provided scalar is a real number. """
    if is_scalar(scalar):
        new_matrix = []
        for i in range(matrix.rows):
            row = []
            for j in range(matrix.cols):
                row += [matrix.matrix[i][j] * scalar]
            new_matrix += [row]
        return Matrix(new_matrix)
    else:
        raise InvalidCalcError(NOT_SCALAR_MESSAGE)


def matrix_multiplication(left_matrix: Matrix, right_matrix: Matrix) -> Matrix:
    """ Returns a new matrix derived from multiplying left_matrix and right_matrix, provided they're compatible. """
    if valid_matrix_multiplication:
        new_matrix = []
        for i in range(left_matrix.rows):
            row = []
            for j in range(right_matrix.cols):
                element_sum = 0
                for k in range(left_matrix.cols):
                    element_sum += left_matrix.matrix[i][k] * right_matrix.matrix[k][j]
                row += [element_sum]
            new_matrix += [row]
        return Matrix(new_matrix)
    else:
        raise InvalidCalcError(INVALID_MATRIX_MULT_MESSAGE)
