from flask import Blueprint, jsonify
from acp_app.services.common import get_team

bp = Blueprint('api_team', __name__)


@bp.route('/api/team')
def team():
    data = [
        {
            'id': m.id,
            'name': m.name,
            'role': m.role,
            'email': m.email,
            'linkedin': m.linkedin,
            'units': [u.strip() for u in (m.units or '').split('|') if u.strip()],
        }
        for m in get_team()
    ]
    return jsonify({'team': data})