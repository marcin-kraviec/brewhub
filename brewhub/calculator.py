import math

class Calculator():

    @staticmethod
    def gravity(gravity_contributions, amounts, efficiency, volume, attenuation):
        gravity_points = []
        n = len(gravity_contributions)
        for i in range(n):
            points = int(str(gravity_contributions)[-2:])
            gravity_points.append(points)

        points_sum = 0
        for i in range(n):
            points_sum += gravity_points[i] * amounts[i] / 2.2

        total = round((points_sum * 0.01 * efficiency) / (volume / 3.78)) / 1000
        og = total + 1
        fg = og - 0.01 * attenuation * og
        return og, fg

    @staticmethod
    def abv(og, fg):
        abv = (og - fg) * 131.25
        return abv

    @staticmethod
    def srm(srms, amounts, volume):
        mcu = 0
        for i in range(len(srms)):
            mcu +=  (amounts[i] / 2.2) * srms[i] / (volume / 3.78)

        srm = 1.4922 * (mcu ** 0.6859)
        return srm

    @staticmethod
    def ibu(alpha_acids, time, amounts, volume, og):
        ibu = 0
        for i in range(len(alpha_acids)):
            utilization = ((1.0 - math.exp(-0.04 * time[i])) / 4.15) * (1.65 * math.pow(0.000125, (og - 1.0)))
            ibu += utilization * (0.01 * alpha_acids * amounts / 0.035274 * 0.7489) / (volume / 3.78)
        return ibu

