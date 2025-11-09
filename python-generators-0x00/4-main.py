
stream_ages_module = __import__("4-stream_ages")


def compute_average_age():
    """
        Compute the average age of users using the streaming generator.
    """
    total_age = 0
    count = 0
    
    for age in stream_ages_module.stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("No users found.")
        return

    # calculate avergae age
    average_age = total_age/age
    print(f"Average age of {count} users: {average_age:.2f}")


if __name__ == "__main__":
    compute_average_age()