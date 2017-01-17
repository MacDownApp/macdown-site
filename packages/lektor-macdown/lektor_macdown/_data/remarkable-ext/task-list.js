function taskMarker(state, silent) {
	var pos = state.pos;
	var content, checked;

	// Must immediately follow the open token.
	if (state.tokens.length > 0 &&
				state.tokens[state.tokens.length - 1].type !== 'list_item_open') {
		return false;
	}

	while (state.src.charCodeAt(pos) === 0x20) {	// Skip spaces.
		pos++;
	}

	content = state.src.slice(pos, pos + 3);
	if (content === '[x]') {
		checked = true;
	} else if (content === '[ ]') {
		checked = false;
	} else {
		return false;
	}

	if (silent) {
		return false;
	}
	if (state.level >= state.options.maxNesting) {
		return false;
	}

	state.push({
		type: 'task_marker',
		checked: checked,
		level: state.level
	});
	state.pos = pos + content.length;
	return true;
}

rmkb.inline.ruler.push('task_marker', taskMarker);

rmkb.renderer.rules.task_marker = function (tokens, idx, options, env) {
	var s = '<input type="checkbox"';
	if (tokens[idx].checked === true) {
		if (options.xhtmlOut) {
			s += ' checked="checked"';
		} else {
			s += ' checked';
		}
	}
	if (options.xhtmlOut) {
		s += ' disabled="disabled" />';
	} else {
		s += ' disabled>';
	}
	return s;
}
