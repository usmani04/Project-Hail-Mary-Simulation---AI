class BayesianKnowledge:

    def __init__(self):
        self.beliefs = {
            "astrophage_understood":   0.15,
            "taumoeba_found":          0.10,
            "star_map_accurate":       0.25,
            "fuel_source_identified":  0.10,
            "communication_possible":  0.15,
        }

        self.likelihoods = {
            "sample_collected": {
                "astrophage_understood":  0.55,
                "taumoeba_found":         0.45,
                "fuel_source_identified": 0.30,
            },
            "experiment_success": {
                "astrophage_understood":  0.75,
                "taumoeba_found":         0.65,
                "fuel_source_identified": 0.55,
                "communication_possible": 0.35,
            },
            "experiment_failure": {
                "astrophage_understood":  0.40,
                "taumoeba_found":         0.40,
                "fuel_source_identified": 0.40,
                "communication_possible": 0.40,
            },
            "rocky_shared_data": {
                "star_map_accurate":      0.90,
                "communication_possible": 0.85,
                "astrophage_understood":  0.50,
            },
            "entered_astrophage_zone": {
                "astrophage_understood":  0.40,
                "fuel_source_identified": 0.30,
            },
            "reached_adrian": {
                "taumoeba_found":         0.70,
                "astrophage_understood":  0.40,
            },
        }

    def update(self, observation: str):
        if observation not in self.likelihoods:
            return
        for hypothesis, likelihood in self.likelihoods[observation].items():
            prior = self.beliefs[hypothesis]
            self.beliefs[hypothesis] = round(self._bayes(prior, likelihood), 4)

    def _bayes(self, prior: float, likelihood: float) -> float:
        p_obs = likelihood * prior + (1 - likelihood) * (1 - prior)
        if p_obs == 0:
            return prior
        posterior = (likelihood * prior) / p_obs
        return min(0.97, max(0.05, posterior))

    def knowledge_score(self) -> float:
        return round(sum(self.beliefs.values()) / len(self.beliefs) * 100, 2)

    def most_uncertain(self) -> str:
        return min(self.beliefs, key=lambda h: abs(self.beliefs[h] - 0.5))

    def summary(self) -> dict:
        return {k: round(v, 3) for k, v in self.beliefs.items()}
