import numpy as np
import textmining
import os

def read_logvol(logvol_filename):
    '''
    Take a filename, read the log volality in the file, and 
    return the numpy list of logvol ordered by the CUSIP number
    '''
    file_length = 0
    with open(logvol_filename) as logvol_file:
        current_line = logvol_file.readline()
        while current_line:
            file_length += 1
            current_line = logvol_file.readline()
    logvol = np.zeros(file_length)
    index = 0
    with open(logvol_filename) as logvol_file:
        current_line = logvol_file.readline()
        while current_line:
            curr_logvol = float(current_line.split()[0])
            logvol[index] = curr_logvol
            index += 1
            current_line = logvol_file.readline()
    return logvol

def construct_doc_term_matrix(tok_folders):
    '''
    Take a list of path to folders where tok.mda file is stored, 
    and return 
    1. the numpy NumDoc x NumVocab matrix of doctermatrix
    Document ordered by Folder order and then by CUSIP number
    2. number of document in the last folder
    Folders should not end with "/"
    Folders should be ordered by time
    '''
    tm_tdm = textmining.TermDocumentMatrix() 
    document_count = 0
    document_last_count = 0
    for tok_folder in tok_folders:
        tokfile_list = os.listdir(tok_folder)
        tokfile_list.sort()
        document_last_count = 0
        for tokfile_name in tokfile_list:
            with open(tok_folder + "/" + tokfile_name) as tokfile:
                tm_tdm.add_doc(tokfile.readline())
                document_count += 1
                document_last_count += 1
    np_tdm = 0 
    row_index = -1
    for row in tm_tdm.rows(cutoff=1):
        if row_index < 0:
            np_tdm = np.zeros(shape=(document_count, len(row)))
        else:
            np_tdm[row_index] = row
        row_index += 1
    return np_tdm, document_last_count

def generate_train_test_set(pred_year, num_prev_year):
    '''
    Generate all test/train data, including extra X
    which is the logvol-12 file
    '''
    tok_folder = []
    X_train_extra = np.zeros(0)
    Y_train = np.zeros(0)
    X_test_extra = 0
    Y_test = 0

    minus_file_name = ".logvol.-12.txt" 
    plus_file_name = ".logvol.+12.txt"

    for year in range(pred_year - num_prev_year, pred_year + 1):
        str_year = "../data/" + str(year)
        tok_folder.append(str_year + ".tok")
        if year != pred_year:
            X_train_extra = np.concatenate((X_train_extra, 
                                            read_logvol(str_year + minus_file_name)))
            Y_train = np.concatenate((Y_train, 
                                      read_logvol(str_year + plus_file_name)))
        else:
            X_test_extra = read_logvol(str_year + minus_file_name)
            Y_test = read_logvol(str_year + plus_file_name)

    total_X, test_count = construct_doc_term_matrix(tok_folder)
    X_train = total_X[:-test_count]
    X_test = total_X[-test_count:]
    
    return X_train_extra, X_train, Y_train, X_test_extra, X_test, Y_test