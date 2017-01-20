def getQuery(self, butler, participant_uid):
    stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')
    stackparametersallqs[7]['7aca8cb6c0eef955e2f2549715c6e7aa']['largerthanpivot'] = [38, 30, 36, 87, 88, 17, 93, 65, 27, 15, 89, 18, 90, 35, 50, 7, 2, 56, 94, 64, 98, 40, 75, 12]
    stackparametersallqs[7]['7aca8cb6c0eef955e2f2549715c6e7aa']['count'] = 74
    butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)
    stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')
    utils.debug_print(stackparametersallqs[7])
    return False

