from flask import Blueprint, jsonify
from acp_app.services.common import get_team

bp = Blueprint('api_team', __name__)


@bp.route('/api/team')
def team():
    data = [
        {
            'id': t.id,
            'name': t.name,
            'role': t.role,
            'email': t.email,
            'linkedin': t.linkedin,
            'units': [u.name for u in t.units],
        }
        for t in get_team()
    ]
    return jsonify({'team': data})