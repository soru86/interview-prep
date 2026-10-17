"""Program 44: Merge Mails

Demonstrates using string templates to create personalized mail messages
by merging a template with recipient data.

Reference: https://www.programiz.com/python-programming/examples/merge-mails
"""

from string import Template


def create_mail(template: Template, name: str, amount: str) -> str:
    """Create a personalized mail message using string substitution.

    Args:
        template: A string Template object.
        name: The recipient's name.
        amount: The amount to display in the message.

    Returns:
        The personalized mail string.
    """
    return template.substitute(name=name, amount=amount)


def main() -> None:
    """Demonstrate merging mails with a template and recipient data."""
    template_text = """Dear $name,

Thank you for your recent purchase of $$${amount}.

We appreciate your business and look forward to serving you again.

Best regards,
The Store Team
"""
    template = Template(template_text)

    recipients = [
        {"name": "Alice", "amount": "150.00"},
        {"name": "Bob", "amount": "230.50"},
        {"name": "Charlie", "amount": "89.99"},
    ]

    for recipient in recipients:
        mail = create_mail(template, **recipient)
        print(mail)
        print("-" * 50)


if __name__ == "__main__":
    main()
