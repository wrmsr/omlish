"""
https://www.freedesktop.org/software/systemd/man/latest/systemd.syntax.html
https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html
https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html


==

https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files

==

Systemd categories units according to the type of resource they describe. The easiest way to determine the type of a unit is with its type suffix, which is appended to the end of the resource name. The following list describes the types of units available to systemd:

==

[Unit]
Description=Example Background Service
After=network.target

[Service]
ExecStart=/home/ec2-user/example_service.sh
Restart=always
User=ec2-user
WorkingDirectory=/usr/local/bin
StandardOutput=append:/var/log/example_service.log
StandardError=append:/var/log/example_service.log

[Install]
WantedBy=multi-user.target
"""
import dataclasses as dc
import enum
import typing as ta


class SystemdSettingName:
    def __new__(cls, *args, **kwargs):
        raise TypeError


class SystemdUnitType(enum.Enum):
    # A service unit describes how to manage a service or application on the server. This will include how to start or
    # stop the service, under which circumstances it should be automatically started, and the dependency and ordering
    # information for related software.
    SERVICE = enum.auto()

    # A socket unit file describes a network or IPC socket, or a FIFO buffer that systemd uses for socket-based
    # activation. These always have an associated .service file that will be started when activity is seen on the socket
    # that this unit defines.
    SOCKET = enum.auto()

    # A unit that describes a device that has been designated as needing systemd management by udev or the sysfs
    # filesystem. Not all devices will have .device files. Some scenarios where .device units may be necessary are for
    # ordering, mounting, and accessing the devices.
    DEVICE = enum.auto()

    # This unit defines a mountpoint on the system to be managed by systemd. These are named after the mount path, with
    # slashes changed to dashes. Entries within /etc/fstab can have units created automatically.
    MOUNT = enum.auto()

    # An .automount unit configures a mountpoint that will be automatically mounted. These must be named after the mount
    # point they refer to and must have a matching .mount unit to define the specifics of the mount.
    AUTOMOUNT = enum.auto()

    # This unit describes swap space on the system. The name of these units must reflect the device or file path of the
    # space.
    SWAP = enum.auto()

    # A target unit is used to provide synchronization points for other units when booting up or changing states. They
    # also can be used to bring the system to a new state. Other units specify their relation to targets to become tied
    # to the target’s operations.
    TARGET = enum.auto()

    # This unit defines a path that can be used for path-based activation. By default, a .service unit of the same base
    # name will be started when the path reaches the specified state. This uses inotify to monitor the path for changes.
    PATH = enum.auto()

    # A .timer unit defines a timer that will be managed by systemd, similar to a cron job for delayed or scheduled
    # activation. A matching unit will be started when the timer is reached.
    TIMER = enum.auto()

    # A .snapshot unit is created automatically by the systemctl snapshot command. It allows you to reconstruct the
    # current state of the system after making changes. Snapshots do not survive across sessions and are used to roll
    # back temporary states.
    SNAPSHOT = enum.auto()

    # A .slice unit is associated with Linux Control Group nodes, allowing resources to be restricted or assigned to any
    # processes associated with the slice. The name reflects its hierarchical position within the cgroup tree. Units are
    # placed in certain slices by default depending on their type.
    SLICE = enum.auto()

    # Scope units are created automatically by systemd from information received from its bus interfaces. These are used
    # to manage sets of system processes that are created externally.
    SCOPE = enum.auto()


@dc.dataclass(frozen=True)
class SystemdUnitSection:
    # This directive can be used to describe the name and basic functionality of the unit. It is returned by various
    # systemd tools, so it is good to set this to something short, specific, and informative.
    description: ta.Optional[str] = None

    # This directive provides a location for a list of URIs for documentation. These can be either internally available
    # man pages or web accessible URLs. The systemctl status command will expose this information, allowing for easy
    # discoverability.
    documentation: ta.Optional[str] = None

    # This directive lists any units upon which this unit essentially depends. If the current unit is activated, the
    # units listed here must successfully activate as well, else this unit will fail. These units are started in
    # parallel with the current unit by default.
    requires: ta.Optional[str] = None

    # This directive is similar to Requires=, but less strict. Systemd will attempt to start any units listed here when
    # this unit is activated. If these units are not found or fail to start, the current unit will continue to function.
    # This is the recommended way to configure most dependency relationships. Again, this implies a parallel activation
    # unless modified by other directives.
    wants: ta.Optional[str] = None

    # This directive is similar to Requires=, but also causes the current unit to stop when the associated unit
    # terminates.
    binds_to: ta.Optional[str] = None

    # The units listed in this directive will not be started until the current unit is marked as started if they are
    # activated at the same time. This does not imply a dependency relationship and must be used in conjunction with one
    # of the above directives if this is desired.
    before: ta.Optional[str] = None

    # The units listed in this directive will be started before starting the current unit. This does not imply a
    # dependency relationship and one must be established through the above directives if this is required.
    after: ta.Optional[str] = None

    # This can be used to list units that cannot be run at the same time as the current unit. Starting a unit with this
    # relationship will cause the other units to be stopped.
    conflicts: ta.Optional[str] = None

    # There are a number of directives that start with Condition which allow the administrator to test certain
    # conditions prior to starting the unit. This can be used to provide a generic unit file that will only be run when
    # on appropriate systems. If the condition is not met, the unit is gracefully skipped.
    condition: ta.Optional[str] = None

    # Similar to the directives that start with Condition, these directives check for different aspects of the running
    # environment to decide whether the unit should activate. However, unlike the Condition directives, a negative
    # result causes a failure with this directive.
    assert_: ta.Optional[str] = dc.field(default=None, metadata={SystemdSettingName: 'assert'})


@dc.dataclass(frozen=True)
class SystemdInstallSection:
    # The WantedBy= directive is the most common way to specify how a unit should be enabled. This directive allows you
    # to specify a dependency relationship in a similar way to the Wants= directive does in the [Unit] section. The
    # difference is that this directive is included in the ancillary unit allowing the primary unit listed to remain
    # relatively clean. When a unit with this directive is enabled, a directory will be created within
    # /etc/systemd/system named after the specified unit with .wants appended to the end. Within this, a symbolic link
    # to the current unit will be created, creating the dependency. For instance, if the current unit has
    # WantedBy=multi-user.target, a directory called multi-user.target.wants will be created within /etc/systemd/system
    # (if not already available) and a symbolic link to the current unit will be placed within. Disabling this unit
    # removes the link and removes the dependency relationship.
    wanted_by: ta.Optional[str] = None

    # This directive is very similar to the WantedBy= directive, but instead specifies a required dependency that will
    # cause the activation to fail if not met. When enabled, a unit with this directive will create a directory ending
    # with .requires.
    required_by: ta.Optional[str] = None

    # This directive allows the unit to be enabled under another name as well. Among other uses, this allows multiple
    # providers of a function to be available, so that related units can look for any provider of the common aliased
    # name.
    alias: ta.Optional[str] = None

    # This directive allows units to be enabled or disabled as a set. Supporting units that should always be available
    # when this unit is active can be listed here. They will be managed as a group for installation tasks.
    also: ta.Optional[str] = None

    # For template units (covered later) which can produce unit instances with unpredictable names, this can be used as
    # a fallback value for the name if an appropriate name is not provided.
    default_instance: ta.Optional[str] = None


class SystemdServiceType(enum.Enum):
    # The main process of the service is specified in the start line. This is the default if the Type= and Busname=
    # directives are not set, but the ExecStart= is set. Any communication should be handled outside of the unit through
    # a second unit of the appropriate type (like through a .socket unit if this unit must communicate using sockets).
    SIMPLE = enum.auto()

    # This service type is used when the service forks a child process, exiting the parent process almost immediately.
    # This tells systemd that the process is still running even though the parent exited.
    FORKING = enum.auto()

    # This type indicates that the process will be short-lived and that systemd should wait for the process to exit
    # before continuing on with other units. This is the default Type= and ExecStart= are not set. It is used for
    # one-off tasks.
    ONESHOT = enum.auto()

    # This indicates that unit will take a name on the D-Bus bus. When this happens, systemd will continue to process
    # the next unit.
    DBUS = enum.auto()

    # This indicates that the service will issue a notification when it has finished starting up. The systemd process
    # will wait for this to happen before proceeding to other units.
    NOTIFY = enum.auto()

    # This indicates that the service will not be run until all jobs are dispatched.
    IDLE = enum.auto()


@dc.dataclass(frozen=True)
class SystemdServiceSection:
    # One of the basic things that should be specified within the [Service] section is the Type= of the service. This
    # categorizes services by their process and daemonizing behavior. This is important because it tells systemd how to
    # correctly manage the servie and find out its state.
    type: SystemdServiceType = SystemdServiceType.SIMPLE

    #

    # This directive is commonly used with the oneshot type. It indicates that the service should be considered active
    # even after the process exits.
    remain_after_exit: ta.Optional[str] = None

    # If the service type is marked as “forking”, this directive is used to set the path of the file that should contain
    # the process ID number of the main child that should be monitored.
    pidfile: ta.Optional[str] = dc.field(default=None, metadata={SystemdSettingName: 'PIDFile'})

    # This directive should be set to the D-Bus bus name that the service will attempt to acquire when using the “dbus”
    # service type.
    bus_name: ta.Optional[str] = None

    # This specifies access to the socket that should be used to listen for notifications when the “notify” service type
    # is selected This can be “none”, “main”, or "all. The default, “none”, ignores all status messages. The “main”
    # option will listen to messages from the main process and the “all” option will cause all members of the service’s
    # control group to be processed.
    notify_access: ta.Optional[str] = None

    #

    # This specifies the full path and the arguments of the command to be executed to start the process. This may only
    # be specified once (except for “oneshot” services). If the path to the command is preceded by a dash “-” character,
    # non-zero exit statuses will be accepted without marking the unit activation as failed.
    exec_start: ta.Optional[str] = None

    # This can be used to provide additional commands that should be executed before the main process is started. This
    # can be used multiple times. Again, commands must specify a full path and they can be preceded by “-” to indicate
    # that the failure of the command will be tolerated.
    exec_start_pre: ta.Optional[str] = None

    # This has the same exact qualities as ExecStartPre= except that it specifies commands that will be run after the
    # main process is started.
    exec_start_post: ta.Optional[str] = None

    # This optional directive indicates the command necessary to reload the configuration of the service if available.
    exec_reload: ta.Optional[str] = None

    # This indicates the command needed to stop the service. If this is not given, the process will be killed
    # immediately when the service is stopped.
    exec_stop: ta.Optional[str] = None

    # This can be used to specify commands to execute following the stop command.
    exec_stop_post: ta.Optional[str] = None

    # If automatically restarting the service is enabled, this specifies the amount of time to wait before attempting to
    # restart the service.
    restart_sec: ta.Optional[str] = None

    # This indicates the circumstances under which systemd will attempt to automatically restart the service. This can
    # be set to values like “always”, “on-success”, “on-failure”, “on-abnormal”, “on-abort”, or “on-watchdog”. These
    # will trigger a restart according to the way that the service was stopped.
    restart: ta.Optional[str] = None

    # This configures the amount of time that systemd will wait when stopping or stopping the service before marking it
    # as failed or forcefully killing it. You can set separate timeouts with TimeoutStartSec= and TimeoutStopSec= as
    # well.
    timeout_sec: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class SystemdSocketSection:
    # This defines an address for a stream socket which supports sequential, reliable communication. Services that use
    # TCP should use this socket type.
    listen_stream: ta.Optional[str] = None

    # This defines an address for a datagram socket which supports fast, unreliable communication packets. Services that
    # use UDP should set this socket type.
    listen_datagram: ta.Optional[str] = None

    # This defines an address for sequential, reliable communication with max length datagrams that preserves message
    # boundaries. This is found most often for Unix sockets.
    listen_sequential_packet: ta.Optional[str] = None

    # Along with the other listening types, you can also specify a FIFO buffer instead of a socket.
    listen_fifo: ta.Optional[str] = None

    #

    # This determines whether an additional instance of the service will be started for each connection. If set to false
    # (the default), one instance will handle all connections.
    accept: ta.Optional[str] = None

    # With a Unix socket, specifies the owner of the socket. This will be the root user if left unset.
    socket_user: ta.Optional[str] = None

    # With a Unix socket, specifies the group owner of the socket. This will be the root group if neither this or the
    # above are set. If only the SocketUser= is set, systemd will try to find a matching group.
    socket_group: ta.Optional[str] = None

    # For Unix sockets or FIFO buffers, this sets the permissions on the created entity.
    socket_mode: ta.Optional[str] = None

    # If the service name does not match the .socket name, the service can be specified with this directive.
    service: ta.Optional[str] = None
