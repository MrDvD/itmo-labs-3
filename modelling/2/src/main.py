import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict

from lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')

    matrix_1 = [['--' for _ in range(24)]
                      for _ in range(24)]
    matrix_1[0][6] = '$p_2\\lambda$'
    matrix_1[0][12] = '$p_1\\lambda$'
    matrix_1[6][0] = '$\\mu$'
    matrix_1[12][0] = '$\\mu$'
    matrix_1[6][18] = '$\\lambda$'
    matrix_1[18][6] = '$\\mu$'
    matrix_1[12][18] = '$\\lambda$'
    matrix_1[18][12] = '$\\mu$'
    matrix_1[18][19] = '$\\lambda$'
    matrix_1[19][18] = '$2\\mu$'
    matrix_1[19][20] = '$\\lambda$'
    matrix_1[20][19] = '$2\\mu$'
    matrix_1[20][21] = '$\\lambda$'
    matrix_1[21][20] = '$2\\mu$'
    matrix_1[21][22] = '$\\lambda$'
    matrix_1[22][21] = '$2\\mu$'
    matrix_1[22][23] = '$\\lambda$'
    matrix_1[23][22] = '$2\\mu$'

    matrix_1[0][0] = '$-\\lambda$'
    matrix_1[6][6] = '$-(\\lambda+\\mu)$'
    matrix_1[12][12] = '$-(\\lambda+\\mu)$'
    matrix_1[18][18] = '$-(\\lambda+2\\mu)$'
    matrix_1[19][19] = '$-(\\lambda+2\\mu)$'
    matrix_1[20][20] = '$-(\\lambda+2\\mu)$'
    matrix_1[21][21] = '$-(\\lambda+2\\mu)$'
    matrix_1[22][22] = '$-(\\lambda+2\\mu)$'
    matrix_1[23][23] = '$-2\\mu$'

    matrix_1 = ReportFiller.clean_absorbing_states(matrix_1, zero_str='--')

    matrix_2 = [['--' for _ in range(16)]
                        for _ in range(16)]

    matrix_2[0][2] = '$p_3\\lambda$'
    matrix_2[0][4] = '$p_2\\lambda$'
    matrix_2[0][8] = '$p_1\\lambda$'
    matrix_2[2][0] = '$\\nu$'
    matrix_2[8][0] = '$\\mu$'
    matrix_2[4][0] = '$\\mu$'

    matrix_2[2][10] = '$\\lambda p_{13}$'
    matrix_2[2][6]  = '$\\lambda p_{23}$'
    matrix_2[6][2]  = '$\\mu$'
    matrix_2[10][2] = '$\\mu$'

    matrix_2[4][12] = '$\\lambda p_{12}$'
    matrix_2[4][6]  = '$\\lambda p_{32}$'
    matrix_2[12][4] = '$\\mu$'
    matrix_2[6][4]  = '$\\nu$'
    matrix_2[5][4]  = '$\\mu$'

    matrix_2[5][13] = '$\\lambda p_{12}$'
    matrix_2[5][7]  = '$\\lambda p_{32}$'
    matrix_2[13][5] = '$\\mu$'
    matrix_2[7][5]  = '$\\nu$'

    matrix_2[6][14] = '$\\lambda$'
    matrix_2[7][6]  = '$\\mu$'
    matrix_2[14][6] = '$\\mu$'

    matrix_2[7][15] = '$\\lambda$'
    matrix_2[15][7] = '$\\mu$'

    matrix_2[8][10] = '$\\lambda p_{31}$'
    matrix_2[8][12] = '$\\lambda p_{21}$'
    matrix_2[10][8] = '$\\nu$'
    matrix_2[12][8] = '$\\mu$'

    matrix_2[10][14] = '$\\lambda$'
    matrix_2[14][10] = '$\\mu$'

    matrix_2[12][14] = '$\\lambda$'
    matrix_2[14][12] = '$\\nu$'
    matrix_2[13][12] = '$\\mu$'

    matrix_2[13][15] = '$\\lambda$'
    matrix_2[15][13] = '$\\nu$'

    matrix_2[14][15] = '$\\lambda$'
    matrix_2[15][14] = '$\\mu$'

    matrix_2[0][0]   = '$-\\lambda$'
    matrix_2[2][2]   = '$-(\\lambda+\\nu)$'
    matrix_2[4][4]   = '$-(\\lambda+\\mu)$'
    matrix_2[5][5]   = '$-(\\lambda+\\mu)$'
    matrix_2[6][6]   = '$-(\\lambda+\\mu+\\nu)$'
    matrix_2[7][7]   = '$-(\\lambda+\\mu+\\nu)$'
    matrix_2[8][8]   = '$-(\\lambda+\\mu)$'
    matrix_2[10][10] = '$-(\\lambda+\\mu+\\nu)$'
    matrix_2[12][12] = '$-(\\lambda+2\\mu)$'
    matrix_2[13][13] = '$-(\\lambda+2\\mu)$'
    matrix_2[14][14] = '$-(\\lambda+2\\mu+\\nu)$'
    matrix_2[15][15] = '$-(2\\mu+\\nu)$'

    matrix_2 = ReportFiller.clean_absorbing_states(matrix_2, zero_str='--')
    
    context: Dict[str, Any] = {
        'variant': cfg['variant'],
        'load_params': cfg['load_params'],
        'system_1': {
            'Pi_1': cfg['load_params']['Pi_1'],
            'Pi_2': cfg['load_params']['Pi_2']+cfg['load_params']['Pi_3'],
        },
        'graph_1': matrix_1,
        'graph_2': matrix_2,
    }

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()