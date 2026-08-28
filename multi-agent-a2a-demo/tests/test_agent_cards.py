from a2a_mail_notify.agents.mailbox import create_mailbox_app, mailbox_agent_card
from a2a_mail_notify.agents.whatsapp import create_whatsapp_app, whatsapp_agent_card
from a2a_mail_notify.config import load_settings


def test_agent_cards_and_apps(tmp_config):
    settings = load_settings()
    mailbox_card = mailbox_agent_card(settings)
    whatsapp_card = whatsapp_agent_card(settings)
    assert mailbox_card.name == "Mailbox Agent"
    assert whatsapp_card.name == "WhatsApp Agent"
    assert any(skill.id == "check_mailbox" for skill in mailbox_card.skills)
    assert any(skill.id == "notify_email" for skill in whatsapp_card.skills)
    mailbox_app = create_mailbox_app(settings)
    whatsapp_app = create_whatsapp_app(settings)
    assert mailbox_app is not None
    assert whatsapp_app is not None
