###
### Random Variate Generator:
### a python class library which generates both discrete and continuous random variates
###
### Sources used: D. Joyce's "Common probability distributions" paper https://mathcs.clarku.edu/~djoyce/ma217/distributions2.pdf
### I used Joyce's paper for its organization (how it grouped the distributions) and to better understand how they related to each other
### To help my learning process, I quoted Joyce's summary of each distribution as the comment on each method.
### Were this anything other than education project, I would remove Joyce's words or seek permission to use them.

### JOYCE: Most computer programming languages have a built in pseudorandom number generator which generates numbers X in the unit interval [0, 1]. Random number generators for
### any other distribution can then computed by applying the inverse of the cumulative distribution function for that distribution to X.

import numpy as np
import math

DEFAULT_SIZE=50000      ### This takes ~ 1 minute (95% of which is on binomial) and provides excellent results.
DEFAULT_SIZE=9999       ### This is speedy and provides decent results.
SEED=12345
MU = 0
SIGMA = 1
PROB = 0.8
LAM = 5
SHAPE = 5
DOF = 2
DISCRETE_LOW = 1
DISCRETE_HIGH = 100


class RV:
    def __init__(self, seed=SEED) -> None:
        self.low = 0.0
        self.high = 1.0
        self.generator = np.random.default_rng(seed=seed)
        self.base = self.get_uniform_continuous()

    def get_base(self):
        return self.base

    def get_hw(self):
        return -np.log(self.base)

    def get_uniform_continuous(self, size=DEFAULT_SIZE):
        """ CONTINUOUS:
        Joyce: In general, a continuous uniform variable X takes values on a curve, surface, or higher
        dimensional region, but here I only consider the case when X takes values in an interval [a, b].
        Being uniform, the probability that X lies in a subinterval is proportional to the length of that subinterval.
        """
        ### For this base distribution Unif(0,1), we'll use numpy's generation.
        ### all others will be calculated from scratch using this Unif(0,1) base.
        return self.generator.uniform(low=self.low, high=self.high, size=size)

    def get_uniform_discrete(self, n=DISCRETE_HIGH):
        """ DISCRETE:
        Joyce: In general, a discrete uniform random variable X can take any finite set as values, but
        here I only consider the case when X takes on integer values from 1 to n, where the parameter
        n is a positive integer. Each value has the same probability, namely 1/n.
        """
        ### multiply a continous uniform by n and take the ceiling function
        unif_discrete = np.ceil(self.base * n)
        return unif_discrete, self._compare_uniform_discrete(high=n)

    def _compare_uniform_discrete(self, low=DISCRETE_LOW, high=DISCRETE_HIGH):
        return np.random.randint(low=low, high=high, size=DEFAULT_SIZE)


    """ DISTRIBUTIONS RELATED TO THE CENTRAL LIMIT THEOREM
    JOYCE: The Central Limit Theorem says sample means and sample sums approach normal distributions as the sample size approaches infinity.
    And so says GOLDSMAN.
    """

    def get_normal(self):
        """ CONTINUOUS:
        The Normal (Gaussian) distribution has mean of 0 and variance of 1 """
        ### Here we will perform the box-muller transformation. Z1 = sqrt(-2*ln(U1). cos(2pi* U2))
        ### We also need to create a distinct second unif base:
        u1 = self.base
        u2 = self.get_uniform_continuous()

        a = np.sqrt(-2 * np.log(u1))
        b = np.cos(2 * np.pi * u2)
        norm = a * b
        return norm, self._compare_normal()

    def _compare_normal(self, mu=MU, sigma=SIGMA):
        return self.generator.normal(mu, sigma, size=DEFAULT_SIZE)


    """ BERNOULLI PROCESSES
    JOYCE: You can ask various questions about a Bernoulli process, and the answers to these questions have various distributions.
    Bernoulli: The Bernoulli distribution, Bernoulli(p), simply says whether one trial is a success.
    Bionomial: If you ask how many successes there will be among n Bernoulli trials, then the answer will have a binomial distribution, Binomial(n, p).
    Geometric: If you ask how many trials it will be to get the first success, then the answer will have a geometric distribution, Geometric(p).

    """

    def get_bernoulli(self, prob=PROB, base=None):
        """ DISCRETE:
        Return a 0 if value is < p, otherwise 1 """

        ### Allows caller to override which base uniform to pass in:
        if base is None:
            base = self.base

        ### setup an array of same size as base, but all zeros
        bernoulli = np.zeros_like(base)

        ### set true/false flags in bern if > or < than prob
        mask = base < prob

        ### update bern with 1's if mask=True
        bernoulli[mask] = 1

        return bernoulli, self._compare_bernoulli(prob)

    def _compare_bernoulli(self, prob=PROB):
        return self.generator.binomial(n=1, p=prob, size=DEFAULT_SIZE)

    def get_binomial(self, prob=PROB, num_trials=DEFAULT_SIZE):
        """ DISCRETE:
        Repeat bernoulli x num_trials times, using a new unif(0,1) each time
        Note: I have observed that this method is inefficient for trial sizes > 500K and results take too long """

        all_trials = []
        for times in range(num_trials):
            unif = self.get_uniform_continuous()
            bernoulli, _ = self.get_bernoulli(prob=prob, base=unif)

            ### How many coin flips in this trial were a 1? sum them, and store:
            all_trials.append(np.sum(bernoulli))

        return np.asarray(all_trials), self._compare_binomial(prob)

    def _compare_binomial(self, prob=PROB):
        return self.generator.binomial(n=len(self.base), p=prob, size=DEFAULT_SIZE)

    def get_geometric(self, prob=PROB):
        """ DISCRETE:
        Joyce: "When independent Bernoulli trials are repeated, each with probability p of success, the
        number of trials X it takes to get the first success has a geometric distribution." """
        ### Allow caller to override defaults, which are otherwise attributes of the class

        a = np.log(self.base)
        b = np.log(1 - prob)
        geom = np.ceil(a/b)
        return geom, self._compare_geometric(prob)

    def _compare_geometric(self, prob):
        return self.generator.geometric(p=prob, size=DEFAULT_SIZE)

    """ POISON PROCESS
    Joyce: You can ask various questions about a Poisson process, and the answers will have various distributions.
    Poisson:     If you ask how many events occur in an interval of length t, then the answer will have a Poisson distribution, Poisson(λt).
    Exponential: If you ask how long until the first event occurs, then the answer will have an exponential distribution, Exponential(λ).
    Gamma:       If you ask how long until the rth event, then the answer will have a gamma distribution, Gamma(λ, r).
    Weibull:     Weibull is a generalization of the Exponential distribution, where beta or shape = 1
    Chi-Squared: A χ2-distribution is actually a special case of a gamma distribution with a fractional value for r. ChiSquared(ν) = Gamma(λ, r) where λ =1/2 and r =ν/2.
    """


    def get_poisson(self, lam=int(LAM), size=DEFAULT_SIZE):
        """ DISCRETE:
        Joyce: When events occur uniformly at random over time at a rate of λ events per unit time, then the random variable X
        giving the number of events in a time interval of length t has a Poisson distribution.
        """
        ### This method requires a decent (10K+) sample size to produce a properly looking distribution
        ### My note: Here we use the Acceptance-Rejection method to obtain an array of Poisson values.
        ### Coding this helped me understand the method from Module 7 much better. In particular, it
        ### is interesting because while we loop through a calculation, in the end we return x:the number of passes,
        ### rather than the value generated. We just loop until the the value is bigger than the uniform its built from
        ### Concern: this is actually different than the Module 7 slides because we're not using the product of uniforms,
        ### just sticking with the original uniform. BUT the result more closely matches Poisson than when I coded out the products. hmmm.

        def get_single_poisson(lam, unif):
            x = 0
            exp_of_neg_lambda = np.exp(-lam)
            value = exp_of_neg_lambda

            while unif > value:
                x += 1
                exp_of_neg_lambda *= lam / x
                value += exp_of_neg_lambda

            return x

        pois_list = [get_single_poisson(lam=lam, unif=u) for u in self.base]
        pois = np.array(pois_list)

        return pois, self._compare_poisson(lam)

    def _compare_poisson(self, lam=LAM):
        return self.generator.poisson(lam=lam, size=DEFAULT_SIZE)

    def get_exponential(self, lam=LAM):
        """ CONTINUOUS:
        Joyce: When events occur uniformly at random over time at a rate of λ events per unit time,
        then the random variable X giving the time to the first event has an exponential distribution.
        """
        print(f"---Building Exponential with lambda {lam}")
        ### When U=Unif(0,1), then Exp(λ) = -1/λ * ln(1-U)
        a = (-1/lam)
        b = np.log(1 - self.base)
        exp = a * b
        return exp, self._compare_exponential(lam)

    def get_exponential_via_weibull(self, lam=LAM):
        """ CONTINUOUS:
        Since weibull generalizes exponential, we can also get a weibull with beta=1 to return an exponential
        """
        print(f"---Building Exponential with Weibull {1/lam} and beta (or shape) 1")
        exp, _ = self.get_weibull(lam=1/lam, beta=1)
        return exp, self._compare_exponential(lam=lam)

    def _compare_exponential(self, lam=LAM):
        """ Note: I have observed that a larger sample size cause numpy generated exponentials to have
            a longer tail, moreso than my self-built one.  Still, the distribution given lam matches. """
        return self.generator.exponential(scale=1/lam, size=DEFAULT_SIZE)

    def get_gamma(self, shape=SHAPE, scale=LAM, size=DEFAULT_SIZE):
        """ CONTINUOUS:
        Joyce: In the same Poisson process for the exponential distribution, the gamma distribution gives
        the time to the rth event. Thus, Exponential(λ) = Gamma(λ, r=1).

        FROM: https://www.educative.io/answers/how-to-model-the-gamma-distribution-in-python :
        The parameter λ>0 is known as the rate or scale parameter. This parameter is the mean rate of an event’s occurrence during one unit.
        The parameter α>0 is known as the shape parameter. This parameter specifies the number of events being modeled.

        : input scale: the Lambda, or mean rate of occurence in one time unit. Some formulas call for inverse scale β = 1/θ, also called rate here I've used λ
        : input shape: number of events for each individual gamma element being modeled
        : input  size: how many gammas to generate
        """
        print(f"Generating Gamma Dist with lambda/scale: {scale}, shape: {shape}, of size {size}")
        gamma_list = []
        for _ in range(size):
            ### Get a new uniform dist for each iteration:
            base=self.get_uniform_continuous(math.ceil(shape))

            a = -scale
            b = np.log(np.prod(base))
            exp = a * b
            gamma_list.append(exp)

        gamma = np.array(gamma_list)
        return gamma, self._compare_gamma(shape=shape, scale=scale)

    def _compare_gamma(self, shape=SHAPE, scale=LAM):
        return self.generator.gamma(shape=shape, scale=scale, size=DEFAULT_SIZE)

    def get_weibull(self, lam=LAM, beta=SHAPE):
        """ CONTINUOUS:
        My Notes from lecture: Weibull is a generalization of the Exponential distribution.
        In fact when beta=1, this is the exponential distribution
        a = scale
        b = shape
        """
        print(f"---Building Weibull with lambda {lam} and beta (or shape) {beta}")
        a = -lam
        b = np.log(1 - self.base)
        ### c = np.power(b, 1/beta)
        ### Numpy did not like ^ my formulation for c. This stack overflow suggested the following change: https://stackoverflow.com/questions/45384602/numpy-runtimewarning-invalid-value-encountered-in-power
        c = np.sign(b) * (np.abs(b)) ** (1 / beta)
        weibull = a * c

        return weibull, self._compare_weibull(lam=lam, beta=beta)

    def _compare_weibull(self, lam=LAM, beta=SHAPE):
        return self.generator.weibull(beta, size=DEFAULT_SIZE) * lam

    def get_chi_squared(self, lam=LAM, dof=DOF):
        """ CONTINUOUS:
        Joyce:  This is the distribution for the sum of the squares of ν independent standard normal distributions.
        The parameter ν, the number of “degrees of freedom,” is a positive integer. A χ2-distribution is actually a
        special case of a gamma distribution with a fractional value for r.
        ChiSquared(ν) = Gamma(λ, r) where λ =1/2 and r =ν/2.

        FROM: https://www.mathworks.com/help/stats/gamma-distribution.html :
        The chi-square distribution is equal to the gamma distribution with 2a = ν and b = 2.
        (where) The gamma distribution is a two-parameter continuous distribution that has parameters a (shape) and b (scale).
        so here I call on gamma with shape = dof/2 and scale = 2 (which is inverse of λ, 1/2)
        """
        lam = 0.5
        r = dof/2

        ### redefine terms for clarity
        scale = 1/lam
        shape = r

        print(f"---Building chi_squared with Gamma, setting scale to {scale} and shape to degrees of freedom/2: {shape}")

        chi, _ = self.get_gamma(shape=shape, scale=scale, size=DEFAULT_SIZE)
        return chi, self._compare_chi(k=dof, size=DEFAULT_SIZE)

    def _compare_chi(self, k=DOF, size=DEFAULT_SIZE):
        return self.generator.chisquare(k, size)