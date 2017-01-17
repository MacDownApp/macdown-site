function mathBlock(state, startLine, endLine, silent) {
  var starter, ender, nextLine, mem;
  var haveEndMarker = false;
  var pos = state.bMarks[startLine] + state.tShift[startLine];
  var max = state.eMarks[startLine];

  starter = state.src.slice(pos, max).trim();
  if (starter === '\\\\[') {
    ender = '\\\\]';
  } else {
    return false;
  }

  // Start is found. Can validate.
  if (silent) {
    return true;
  }

  nextLine = startLine;
  while (true) {
    nextLine++;
    if (nextLine >= endLine) {
      // Unclosed block should be autoclosed by end of document.
      // Also block seems to be autoclosed by end of parent.
      break;
    }

    pos = mem = state.bMarks[nextLine] + state.tShift[nextLine];
    max = state.eMarks[nextLine];

    if (pos < max && state.tShift[nextLine] < state.blkIndent) {
      // Non-empty line with negative indent should stop the list:
      // - \\[
      //  test
      break;
    }

    if (state.src.slice(pos, max).trim() !== ender) {
      continue;
    }

    if (state.tShift[nextLine] - state.blkIndent >= 4) {
      // Closing marker should be indented less than 4 spaces.
      continue;
    }

    haveEndMarker = true;
    break;
  }

  state.line = nextLine + (haveEndMarker ? 1 : 0);
  state.tokens.push({
    type: 'math_block',
    content: state.getLines(
      startLine, nextLine, 0, false).substr(starter.length).trim(),
    lines: [ startLine, state.line ],
    level: state.level
  });

  return true;
}

rmkb.block.ruler.before('paragraph', 'math_block', mathBlock);

rmkb.renderer.rules.math_block = function (tokens, idx, options, env) {
  return (
  		'<div class="katex-rendered">' +
      katex.renderToString(tokens[idx].content, true, false) +
      '</div>');
};
