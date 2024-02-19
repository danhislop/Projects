###
### Random Variate Generator:
### User facing code to get RV's from the RV Class
###

from rvgen import RV
import matplotlib.pyplot as plt

DISTRIBUTION_FUNCTION_NAMES = {
    'uniform_discrete': RV.get_uniform_discrete,
    'normal': RV.get_normal,
    'bernoulli': RV.get_bernoulli,
    'binomial': RV.get_binomial,
    'chi_squared': RV.get_chi_squared,
    'exponential': RV.get_exponential,
    'exponential_via_weibull': RV.get_exponential_via_weibull,
    'gamma': RV.get_gamma,
    'geometric': RV.get_geometric,
    'poisson': RV.get_poisson,
    'weibull': RV.get_weibull,
    'all': 'working to create all distributions...',
    'exit': 'preparing to exit..'
}

class UncallableDistributionException(Exception): pass

def get_distribution_function_name(distribution, distribution_function_names=DISTRIBUTION_FUNCTION_NAMES):
    """ relates a common name to a function name: given a string named distribution,
        return the name of corresponding function to generate np_gen distribution """

    function_name = distribution_function_names.get((distribution), "not_found")
    if function_name == "not_found":
        raise UncallableDistributionException("Error: no process exists for a distribution named: " + distribution)
    else:
        return function_name

def get_plot_name(distribution):
    return 'dist_' + distribution + '.png'

def plot_dual_arrays(array1, array2, distribution, bins=10):
    """ Plot two histograms side by side. """
    # create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # plot the first histogram
    ax1.hist(array1, bins=bins, color='blue', alpha=0.5)
    ax1.set_title('My generated ' + distribution)

    # plot the second histogram
    ax2.hist(array2, bins=bins, color='green', alpha=0.5)
    ax2.set_title('Numpy generated ' + distribution)

    # display the figure
    plt.savefig(get_plot_name(distribution=distribution))
    plt.close()

def iterate_chosen_distributions(distributions_to_get, rv):
    ## Generate all requested distributions
    for distribution in distributions_to_get:
        distribution_function = get_distribution_function_name(distribution)
        print(f"\n---Building {distribution} distribution... ")
        my_gen, np_gen = distribution_function(rv)
        print(my_gen, f"\nThe {distribution} array returned is of size {my_gen.size} and its plot has been saved to {get_plot_name(distribution)}" )
        plot_dual_arrays(my_gen, np_gen, distribution=distribution)


# Define the menu function
def menu(rv):
    # Offer options to the user
    print("\nWhich distribution would you like me to generate from the uniform?")
    for key, value in DISTRIBUTION_FUNCTION_NAMES.items():
        print(f"{key}")

    # Get user input
    choice = input("Choose an option by typing the name: ")

    # Execute the chosen option
    if choice in DISTRIBUTION_FUNCTION_NAMES:
        print(f"Building the {DISTRIBUTION_FUNCTION_NAMES[choice]} distribution")

        if choice == 'all':
            choice = list(DISTRIBUTION_FUNCTION_NAMES.keys())

            ## remove the 'all' and 'exit' menu items since they aren't actually distributions
            choice.pop(-1)
            choice.pop(-1)
        elif choice == 'exit':
            exit()
        else:
            choice = [choice]
        print('Received this input: ', choice)
        iterate_chosen_distributions(choice, rv)

    else:
        print("That's an invalid choice.")


if __name__ == "__main__":
    """ Launch RV getter """

    ### Create the Generator and base object
    rv = RV()
    distribution = "Base uniform continuous"
    print(f"\n---Building {distribution} distribution first... ")
    my_gen = rv.get_base()

    print(my_gen, f"\nThe {distribution} returned is of size {my_gen.size}. To change this size, edit DEFAULT_SIZE in rvgen.py" )
    print(f"For each distribution that is built, all elements of the distribution will be plotted and saved to a .png file. ")
    print(f"The plot will show the generated function using the formula in the code, alongside a numpy generated one to compare.")

    ### Run the menu
    while True:
        menu(rv=rv)
