//usr/bin/true; exec om java run "$0" "$@"
/* @omlish-jdeps [
    "com.google.inject:guice:7.0.0"
] */
package com.wrmsr;

import com.google.inject.AbstractModule;
import com.google.inject.Guice;
import com.google.inject.Inject;
import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.Provider;
import com.google.inject.Provides;
import com.google.inject.ProvisionException;
import com.google.inject.Singleton;
import com.google.inject.TypeLiteral;
import com.google.inject.matcher.Matchers;
import com.google.inject.multibindings.MapBinder;
import com.google.inject.multibindings.Multibinder;
import com.google.inject.name.Named;
import com.google.inject.name.Names;
import com.google.inject.spi.InjectionListener;
import com.google.inject.spi.TypeEncounter;
import com.google.inject.spi.TypeListener;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Single-file Guice demo.
 * <p>
 * Demonstrates:
 * - constructor injection
 * - field injection
 * - method injection
 * - explicit bindings
 * - @Provides methods
 * - @Named bindings
 * - singleton scope
 * - Provider<T>
 * - Optional injection
 * - multibindings: Set and Map
 * - generic binding via TypeLiteral
 * - injection listeners (TypeListener + InjectionListener)
 * <p>
 * Not included:
 * - AOP / method interceptors
 */
public class GuiceDemo
{

    public static void main(String[] args)
    {
        Injector injector = Guice.createInjector(
                new CoreModule(),
                new PluginModule(),
                new ListenerModule(),
                new SessionModule()
        );

        System.out.println("== basic object graph ==");
        App app = injector.getInstance(App.class);
        app.run();

        System.out.println();
        System.out.println("== singleton scope demo ==");
        ClockService c1 = injector.getInstance(ClockService.class);
        ClockService c2 = injector.getInstance(ClockService.class);
        System.out.println("ClockService same instance? " + (c1 == c2));

        System.out.println();
        System.out.println("== provider demo ==");
        SessionFactory sessionFactory = injector.getInstance(SessionFactory.class);
        System.out.println("new session id = " + sessionFactory.create().id());
        System.out.println("new session id = " + sessionFactory.create().id());

        System.out.println();
        System.out.println("== direct multibinding access ==");
        Set<Plugin> plugins = injector.getInstance(Key.get(new TypeLiteral<Set<Plugin>>(){}));
        for (Plugin plugin : plugins) {
            System.out.println("plugin: " + plugin.name());
        }

        Map<String, Command> commands = injector.getInstance(Key.get(new TypeLiteral<Map<String, Command>>(){}));
        System.out.println("commands = " + commands.keySet());

        System.out.println();
        System.out.println("== generic binding via TypeLiteral ==");
        StringRepository repo = injector.getInstance(StringRepository.class);
        repo.put("hello", "world");
        repo.put("guice", "demo");
        System.out.println("repo contents = " + repo.snapshot());

        System.out.println();
        System.out.println("== optional binding/injection ==");
        OptionalConsumer optionalConsumer = injector.getInstance(OptionalConsumer.class);
        optionalConsumer.print();

        System.out.println();
        System.out.println("== failure example ==");
        try {
            injector.getInstance(BadConsumer.class);
        }
        catch (ProvisionException e) {
            System.out.println("expected failure: " + e.getMessage().split("\n")[0]);
        }
    }

    /* modules */

    static final class CoreModule
            extends AbstractModule
    {
        @Override
        protected void configure()
        {
            bind(Config.class).toInstance(new Config("demo-app", 8080, true));

            bind(Database.class).to(InMemoryDatabase.class).in(Singleton.class);
            bind(MessageService.class).to(ConsoleMessageService.class);
            bind(ClockService.class).in(Singleton.class);

            bind(String.class).annotatedWith(Names.named("appName")).toInstance("Guice Single File Demo");
            bind(Integer.class).annotatedWith(Names.named("maxConnections")).toInstance(32);

            bind(new TypeLiteral<Repository<String, String>>(){})
                    .to(new TypeLiteral<InMemoryRepository<String, String>>(){})
                    .in(Singleton.class);

            // Bind Optional<String> explicitly so OptionalConsumer can show it.
            bind(new TypeLiteral<Optional<String>>(){})
                    .annotatedWith(Names.named("banner"))
                    .toInstance(Optional.of("welcome from Optional<String> binding"));
        }

        @Provides
        @Singleton
        StartupInfo provideStartupInfo(
                Config config,
                @Named("appName") String appName,
                ClockService clock
        )
        {
            return new StartupInfo(
                    appName,
                    config.port(),
                    clock.now()
            );
        }

        @Provides
        @Named("dbUrl")
        String provideDbUrl(Config config)
        {
            return "mem://" + config.appName() + ":" + config.port();
        }
    }

    static final class PluginModule
            extends AbstractModule
    {
        @Override
        protected void configure()
        {
            Multibinder<Plugin> pluginBinder = Multibinder.newSetBinder(binder(), Plugin.class);
            pluginBinder.addBinding().to(LoggingPlugin.class);
            pluginBinder.addBinding().to(MetricsPlugin.class);
            pluginBinder.addBinding().to(AuditPlugin.class);

            MapBinder<String, Command> commandBinder = MapBinder.newMapBinder(binder(), String.class, Command.class);
            commandBinder.addBinding("hello").to(HelloCommand.class);
            commandBinder.addBinding("time").to(TimeCommand.class);
            commandBinder.addBinding("plugins").to(PluginsCommand.class);
        }
    }

    static final class ListenerModule
            extends AbstractModule
    {
        @Override
        protected void configure()
        {
            bindListener(
                    Matchers.any(),
                    new TypeListener()
                    {
                        @Override
                        public <I> void hear(com.google.inject.TypeLiteral<I> type, TypeEncounter<I> encounter)
                        {
                            Class<? super I> raw = type.getRawType();

                            if (raw.isAnnotationPresent(TraceCreation.class)) {
                                encounter.register((InjectionListener<I>) injectee ->
                                        System.out.println("[InjectionListener] injected " + raw.getSimpleName()));
                            }

                            if (Lifecycle.class.isAssignableFrom(raw)) {
                                encounter.register((InjectionListener<I>) injectee ->
                                        ((Lifecycle) injectee).afterInjection());
                            }
                        }
                    }
            );
        }
    }

    /* app */

    @TraceCreation
    static final class App
            implements Lifecycle
    {
        private final StartupInfo startupInfo;
        private final Database database;
        private final Set<Plugin> plugins;
        private final Map<String, Command> commands;

        @Inject
        @Named("appName")
        String appName;  // field injection demo

        private MessageService messageService;
        private boolean methodInjected;

        @Inject
        App(
                StartupInfo startupInfo,
                Database database,
                Set<Plugin> plugins,
                Map<String, Command> commands
        )
        {
            this.startupInfo = startupInfo;
            this.database = database;
            this.plugins = plugins;
            this.commands = commands;
        }

        @Inject
        void setMessageService(MessageService messageService)
        {  // method injection demo
            this.messageService = messageService;
            this.methodInjected = true;
        }

        @Override
        public void afterInjection()
        {
            System.out.println("[Lifecycle] App.afterInjection()");
        }

        void run()
        {
            messageService.send("starting " + appName);
            System.out.println("startupInfo = " + startupInfo);
            System.out.println("methodInjected = " + methodInjected);

            database.put("status", "ok");
            database.put("startedAt", startupInfo.startedAt().toString());

            System.out.println("plugins:");
            for (Plugin plugin : plugins) {
                plugin.initialize();
            }

            System.out.println("commands:");
            for (Map.Entry<String, Command> e : commands.entrySet()) {
                System.out.println("  " + e.getKey() + " -> " + e.getValue().execute());
            }

            System.out.println("database snapshot = " + database.snapshot());
        }
    }

    /* config / value objects */

    record Config(String appName, int port, boolean devMode)
    {
    }

    record StartupInfo(String appName, int port, Instant startedAt)
    {
    }

    record Session(int id)
    {
    }

    /* marker annotations / lifecycle */

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target({java.lang.annotation.ElementType.TYPE})
    @interface TraceCreation
    {
    }

    interface Lifecycle
    {
        void afterInjection();
    }

    /* services */

    interface MessageService
    {
        void send(String message);
    }

    static final class ConsoleMessageService
            implements MessageService
    {
        @Override
        public void send(String message)
        {
            System.out.println("[message] " + message);
        }
    }

    @Singleton
    static final class ClockService
    {
        Instant now()
        {
            return Instant.now();
        }
    }

    static final class SessionFactory
    {
        private final Provider<Session> sessionProvider;

        @Inject
        SessionFactory(Provider<Session> sessionProvider)
        {
            this.sessionProvider = sessionProvider;
        }

        Session create()
        {
            return sessionProvider.get();
        }
    }

    static final class SessionProvider
            implements Provider<Session>
    {
        private final AtomicInteger nextId = new AtomicInteger(1);

        @Override
        public Session get()
        {
            return new Session(nextId.getAndIncrement());
        }
    }

    /* database */

    interface Database
    {
        void put(String key, String value);

        Map<String, String> snapshot();
    }

    @Singleton
    static final class InMemoryDatabase
            implements Database
    {
        private final Map<String, String> map = new LinkedHashMap<>();

        @Inject
        InMemoryDatabase(@Named("dbUrl") String dbUrl)
        {
            System.out.println("InMemoryDatabase created with url = " + dbUrl);
        }

        @Override
        public void put(String key, String value)
        {
            map.put(key, value);
        }

        @Override
        public Map<String, String> snapshot()
        {
            return new LinkedHashMap<>(map);
        }
    }

    /* plugins / multibindings */

    interface Plugin
    {
        String name();

        void initialize();
    }

    static final class LoggingPlugin
            implements Plugin
    {
        private final MessageService messageService;

        @Inject
        LoggingPlugin(MessageService messageService)
        {
            this.messageService = messageService;
        }

        @Override
        public String name()
        {
            return "logging";
        }

        @Override
        public void initialize()
        {
            messageService.send("plugin init: logging");
        }
    }

    static final class MetricsPlugin
            implements Plugin
    {
        @Override
        public String name()
        {
            return "metrics";
        }

        @Override
        public void initialize()
        {
            System.out.println("[plugin] init metrics");
        }
    }

    static final class AuditPlugin
            implements Plugin
    {
        @Override
        public String name()
        {
            return "audit";
        }

        @Override
        public void initialize()
        {
            System.out.println("[plugin] init audit");
        }
    }

    /* commands / map multibindings */

    interface Command
    {
        String execute();
    }

    static final class HelloCommand
            implements Command
    {
        private final String appName;

        @Inject
        HelloCommand(@Named("appName") String appName)
        {
            this.appName = appName;
        }

        @Override
        public String execute()
        {
            return "hello from " + appName;
        }
    }

    static final class TimeCommand
            implements Command
    {
        private final ClockService clock;

        @Inject
        TimeCommand(ClockService clock)
        {
            this.clock = clock;
        }

        @Override
        public String execute()
        {
            return clock.now().toString();
        }
    }

    static final class PluginsCommand
            implements Command
    {
        private final Set<Plugin> plugins;

        @Inject
        PluginsCommand(Set<Plugin> plugins)
        {
            this.plugins = plugins;
        }

        @Override
        public String execute()
        {
            StringBuilder sb = new StringBuilder();
            boolean first = true;
            for (Plugin plugin : plugins) {
                if (!first) {
                    sb.append(", ");
                }
                sb.append(plugin.name());
                first = false;
            }
            return sb.toString();
        }
    }

    /* generic repository / TypeLiteral */

    interface Repository<K, V>
    {
        void put(K key, V value);

        V get(K key);

        Map<K, V> snapshot();
    }

    @Singleton
    static final class InMemoryRepository<K, V>
            implements Repository<K, V>
    {
        private final Map<K, V> map = new LinkedHashMap<>();

        @Override
        public void put(K key, V value)
        {
            map.put(key, value);
        }

        @Override
        public V get(K key)
        {
            return map.get(key);
        }

        @Override
        public Map<K, V> snapshot()
        {
            return new LinkedHashMap<>(map);
        }
    }

    static final class StringRepository
    {
        private final Repository<String, String> repo;

        @Inject
        StringRepository(Repository<String, String> repo)
        {
            this.repo = repo;
        }

        void put(String k, String v)
        {
            repo.put(k, v);
        }

        Map<String, String> snapshot()
        {
            return repo.snapshot();
        }
    }

    /* optional injection */

    static final class OptionalConsumer
    {
        private final Optional<String> banner;

        @Inject
        OptionalConsumer(@Named("banner") Optional<String> banner)
        {
            this.banner = banner;
        }

        void print()
        {
            System.out.println("banner present? " + banner.isPresent());
            banner.ifPresent(s -> System.out.println("banner = " + s));
        }
    }

    /* provider-binding example */

    /* Guice needs the provider binding installed in a module, so we tuck it into this nested class and
       instantiate it from a static helper below. */
    static final class SessionModule
            extends AbstractModule
    {
        @Override
        protected void configure()
        {
            bind(Session.class).toProvider(SessionProvider.class);
        }
    }

    /* failure demo */

    static final class BadConsumer
    {
        @Inject
        BadConsumer(@Named("missingThing") String missingThing)
        {
            System.out.println(missingThing);
        }
    }
}