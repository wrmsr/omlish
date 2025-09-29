"""
TODO:
 - ContentNamespace Example materializable class
"""
import typing as ta

from omlish import lang
from omlish import marshal as msh

from ....content.namespaces import ContentNamespace
from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ....tools.reflect import tool_spec_override
from ..context import tool_todo_context
from ..types import TODO_ITEM_FIELD_DESCS
from ..types import TodoItem


##


class TodoWriteDescriptionChunks(ContentNamespace):
    INTRO: ta.ClassVar[str] = """
        Use this tool to create and manage a structured list of todo items corresponding to subtasks for your current
        session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user. It
        also helps the user understand the progress of the overall task and progress of their requests.
    """

    FIELD_DESCRIPTIONS: ta.ClassVar[str] = f"""
        A todo item is comprised of the following fields:
        - id: {TODO_ITEM_FIELD_DESCS['id']}
        - content: {TODO_ITEM_FIELD_DESCS['content']}
        - priority: {TODO_ITEM_FIELD_DESCS['priority']}
        - status: {TODO_ITEM_FIELD_DESCS['status']}
    """

    WHEN_USING_THIS_TOOL: ta.ClassVar[str] = """
        When using the todo write tool:
        - All items must be present on each use of the tool.
        - All fields except the id field must be present on all items. If not given, the id field will be automatically
          set to a valid integer.
        - The new todo list, including any generated ids, will be returned from the tool.
    """

    STATUS_DESCRIPTIONS: ta.ClassVar[str] = """
        Todo item statuses are as follows:
        - pending: Task not yet started.
        - in_progress: Currently working on (limit to ONE task at a time).
        - completed: Task finished successfully.
        - cancelled: Task no longer needed.
    """

    MANAGING_ITEMS: ta.ClassVar[str] = """
        Manage todo items in the following manner:
        - Update todo item status in real-time as you work.
        - Mark todo items complete IMMEDIATELY after finishing (don't batch completions).
        - Only have ONE todo item task in_progress at any time.
        - Complete current todo item tasks before starting new ones.
        - Cancel todo items that become irrelevant.
    """

    BREAKING_DOWN: ta.ClassVar[str] = """
        Breakdown tasks in the following manner:
        - Create specific, actionable items.
        - Break complex tasks into smaller, manageable steps.
        - Use clear, descriptive task names.
    """

    USE_PROACTIVELY: ta.ClassVar[str] = """
        Use this tool proactively in these scenarios:
        - Complex multi-step tasks - When a task requires 3 or more distinct steps or actions.
        - Non-trivial and complex tasks - Tasks that require careful planning or multiple operations.
        - User explicitly requests todo list - When the user directly asks you to use the todo list.
        - User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated).
        - After receiving new instructions - Immediately capture user requirements as todos. Feel free to edit the todo
          list based on new information.
        - After completing a task - Mark it complete and add any new follow-up tasks
        - When you start working on a new task, mark the todo item as in_progress. Ideally you should only have one todo
          item as in_progress at a time. Complete existing tasks before starting new ones.
    """

    SKIP_USE_WHEN: ta.ClassVar[str] = """
        Skip using this tool when:
        - There is only a single, straightforward task.
        - The task is trivial and tracking it provides no organizational benefit.
        - The task can be completed in less than 3 trivial steps.
        - The task is purely conversational or informational.
    """

    SKIP_WHEN_TRIVIAL: ta.ClassVar[str] = """
        You should not use this tool if there is only one trivial task to do. In this case you are better off just doing
        the task directly.
    """

    EXAMPLES_WHEN_HEADER: ta.ClassVar[str] = """
        ## Examples of WHEN to use the todo list
    """

    EXAMPLE_WHEN_1: ta.ClassVar[str] = """
        <example>
            <user>
                I want to add a dark mode toggle to the application settings. Make sure you run the tests and build when
                you're done!
            </user>
            <assistant>
                I'll help add a dark mode toggle to your application settings. Let me create a todo list to track this
                implementation.
            </assistant>
            <action>
                * Creates todo list with the following items *
                1. Create dark mode toggle component in Settings page
                2. Add dark mode state management (context/store)
                3. Implement CSS-in-JS styles for dark theme
                4. Update existing components to support theme switching
                5. Run tests and build process, addressing any failures or errors that occur

                * Begins working on the first task *
            </action>
            <reasoning>
                The assistant used the todo list because:
                - Adding dark mode is a multi-step feature requiring UI, state management, and styling changes.
                - The user explicitly requested tests and build be run afterward.
                - The assistant inferred that tests and build need to pass by adding "Ensure tests and build succeed" as
                  the final task.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_2: ta.ClassVar[str] = """
        <example>
            <user>
                Help me rename the function getCwd to getCurrentWorkingDirectory across my project
            </user>
            <assistant>
                Let me first search through your codebase to find all occurrences of 'getCwd'.
            </assistant>
            <action>
                * Uses grep or search tools to locate all instances of getCwd in the codebase *
            </action>
            <assistant>
                I've found 15 instances of 'getCwd' across 8 different files. Let me create a todo list to track these
                changes.
            </assistant>
            <action>
                * Creates todo list with specific items for each file that needs updating *
            </action>
            <reasoning>
                The assistant used the todo list because:
                - First, the assistant searched to understand the scope of the task.
                - Upon finding multiple occurrences across different files, it determined this was a complex task with
                  multiple steps.
                - The todo list helps ensure every instance is tracked and updated systematically.
                - This approach prevents missing any occurrences and maintains code consistency.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_3: ta.ClassVar[str] = """
        <example>
            <user>
                I need to implement these features for my e-commerce site: user registration, product catalog, shopping
                cart, and checkout flow.
            </user>
            <assistant>
                I'll help implement these features. First, let's add all the features to the todo list.
            </assistant>
            <action>
                * Creates a todo list breaking down each feature into specific tasks based on the project architecture *
            </action>
            <assistant>
                Let's start with user registration. This will involve creating database models, API endpoints, and
                frontend forms that integrate with your existing authentication system.
            </assistant>
            <reasoning>
                The assistant used the todo list because:
                - The user provided multiple complex features to implement in a comma separated list.
                - The todo list helps organize these large features into manageable tasks.
                - This approach allows for tracking progress across the entire implementation.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_4: ta.ClassVar[str] = """
        <example>
            <user>
                Can you help optimize my React application? It's rendering slowly and has performance issues.
            </user>
            <assistant>
                I'll help optimize your React application. First, let me examine your codebase to identify potential
                performance bottlenecks.
            </assistant>
            <action>
                * Reviews component structure, render patterns, state management, and data fetching *
            </action>
            <assistant>
                After analyzing your codebase, I've identified several performance issues. Let me create a todo list to
                track our optimization efforts.
            </assistant>
            <action>
                * Creates todo list with the following items *
                1. Implement memoization for expensive calculations in ProductList
                2. Add virtualization for long lists in Dashboard
                3. Optimize image loading in Gallery component
                4. Fix state update loops in ShoppingCart
                5. Review bundle size and implement code splitting
            </action>
            <assistant>
                Let's start by implementing memoization for the expensive calculations in your ProductList component.
            </assistant>
            <reasoning>
                The assistant used the todo list because:
                - First, the assistant examined the codebase to identify specific performance issues.
                - Based on this analysis, it identified multiple optimization opportunities.
                - Performance optimization is a non-trivial task requiring multiple steps.
                - The todo list helps methodically track improvements across different components.
                - This systematic approach ensures all performance bottlenecks are addressed.
            </reasoning>
        </example>
    """

    EXAMPLES_WHEN_NOT_HEADER: ta.ClassVar[str] = """
        ## Examples of when NOT to use the todo list
    """

    EXAMPLE_WHEN_NOT_1: ta.ClassVar[str] = """
        <example>
            <user>
                How do I print 'Hello World' in Python?
            </user>
            <assistant>
                In Python, you can print "Hello World" with this simple code:

                    print("Hello World")

                This will output the text "Hello World" to the console when executed.
            </assistant>
            <reasoning>
                The assistant did not use the todo list because this is a single, trivial task that can be completed in
                one step. There's no need to track multiple tasks or steps for such a straightforward request.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_NOT_2: ta.ClassVar[str] = """
        <example>
            <user>
                What does the git status command do?
            </user>
            <assistant>
                The git status command shows the current state of your working directory and staging area. It displays
                which changes have been staged, which haven't, and which files aren't being tracked by Git. This is a
                fundamental command for understanding the current state of your repository before making commits.
            </assistant>
            <reasoning>
                The assistant did not use the todo list because this is an informational request with no actual coding
                task to complete. The user is simply asking for an explanation, not for the assistant to perform
                multiple steps or tasks.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_NOT_3: ta.ClassVar[str] = """
        <example>
            <user>
                Can you add a comment to the calculateTotal function to explain what it does?
            </user>
            <assistant>
                Sure, let me add a comment to the calculateTotal function to explain what it does.
            </assistant>
            <action>
                * Uses the Edit tool to add a comment to the calculateTotal function *
            </action>
            <reasoning>
                The assistant did not use the todo list because this is a single, straightforward task confined to one
                location in the code. Adding a comment doesn't require tracking multiple steps or systematic
                organization.
            </reasoning>
        </example>
    """

    EXAMPLE_WHEN_NOT_4: ta.ClassVar[str] = """
        <example>
            <user>
                Run npm install for me and tell me what happens.
            </user>
            <assistant>
                I'll run the npm install command for you.
            </assistant>
            <action>
                * Executes: npm install *
            </action>
            <assistant>
                The command completed successfully. Here's the output:

                [Output of npm install command]

                All dependencies have been installed according to your package.json file.
            </assistant>
            <reasoning>
                The assistant did not use the todo list because this is a single command execution with immediate
                results. There are no multiple steps to track or organize, making the todo list unnecessary for this
                straightforward task.
            </reasoning>
        </example>
    """

    OUTRO: ta.ClassVar[str] = """
        When in doubt, use this tool. Being proactive with task management demonstrates attentiveness and ensures you
        complete all requirements successfully.
    """


@tool_spec_override(
    desc=TodoWriteDescriptionChunks,
)
def execute_todo_write_tool(todo_items: ta.Sequence[TodoItem]) -> ta.Sequence[TodoItem]:
    if todo_items:
        todo_items = [
            msh.unmarshal(o, TodoItem) if not isinstance(o, TodoItem) else o  # noqa
            for o in todo_items
        ]

    ctx = tool_todo_context()
    out_items = ctx.set_items(todo_items)

    return out_items or []


@lang.cached_function
def todo_write_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(
        execute_todo_write_tool,
        marshal_input=True,
        marshal_output=True,
    )
