from flask import Blueprint, jsonify, request
from acp_app.services.eos_to_english import eos_resolve

bp = Blueprint('api_gcc', __name__)


@bp.route('/api/gcc/eos', methods=['POST'])
def gcc_eos():
    body = request.get_json(force=True, silent=True) or {}

    try:
        eos_type = int(body.get('eos_type', 0))
        mods = [int(body.get(f'eos_mod{i}', 0)) for i in range(1, 9)]
    except (TypeError, ValueError):
        return jsonify({'error': 'All EOS values must be integers'}), 400

    message, step_not_found, _ = eos_resolve(
        eos_type=eos_type,
        eos_mod_1=mods[0],
        eos_mod_2=mods[1],
        eos_mod_3=mods[2],
        eos_mod_4=mods[3],
        eos_mod_5=mods[4],
        eos_mod_6=mods[5],
        eos_mod_7=mods[6],
        eos_mod_8=mods[7],
    )

    return jsonify({'message': message, 'step_not_found': step_not_found})