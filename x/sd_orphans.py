import subprocess


def get_all_user_services():
    """
    Returns a list of service names for the current user by parsing
    'systemctl --user list-units --type=service --all'.
    """
    cmd = [
        "systemctl",
        "--user",
        "list-units",
        "--type=service",
        "--all",
        "--no-legend",
        "--no-pager",
        "--plain",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    services = []
    for line in result.stdout.strip().splitlines():
        # Each line typically looks like:
        # my-service.service    loaded  active running Some description here
        # We just need the first column (the service name).
        parts = line.split(None, 5)
        if parts:
            service_name = parts[0]
            services.append(service_name)
    return services


def is_service_orphaned(service):
    """
    Returns True if 'systemctl --user show <service>' indicates the service is not found.
    We detect this by checking if 'LoadState=not-found'.
    """
    cmd = [
        "systemctl",
        "--user",
        "show",
        service,
        "--property=LoadState",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Output looks like:
    # LoadState=loaded
    # or
    # LoadState=not-found
    for line in result.stdout.splitlines():
        if line.startswith("LoadState="):
            load_state = line.split("=", 1)[1]
            return (load_state == "not-found")
    return False


def main():
    user_services = get_all_user_services()
    orphaned_services = [
        svc for svc in user_services if is_service_orphaned(svc)
    ]

    if orphaned_services:
        print("Orphaned services (no corresponding unit file):")
        for svc in orphaned_services:
            print("  ", svc)
    else:
        print("No orphaned user services found.")


if __name__ == "__main__":
    main()
