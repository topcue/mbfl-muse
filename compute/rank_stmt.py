def rank(top_n):
    with open('../Chart_1/gzoltars/Chart/1/spectra','r') as f:
        data = f.readlines()

        stmt_dict = {}
        for idx, line in enumerate(data):
            stmt_dict[idx+1] = line.strip()
    
    for stmt_rank in top_n:
        print(f'Rank {stmt_rank}: {stmt_dict[stmt_rank]}')

