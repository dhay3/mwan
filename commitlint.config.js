export default {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: {
      headerPattern:
        /^(?:(?::[a-z0-9_+-]+:|\p{Extended_Pictographic}\S*)\s+)?(\w*)(?:\((.*)\))?!?: (.*)$/u,
      headerCorrespondence: ['type', 'scope', 'subject'],
    },
  },
};
