module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true
      }
    }],
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../../../app/frontend/src/$1',
    '^axios$': require.resolve('axios'),
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    '../../../app/frontend/src/**/*.{ts,tsx}',
    '!../../../app/frontend/src/**/*.d.ts'
  ],
  testMatch: [
    '<rootDir>/**/*.test.{ts,tsx}'
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
  ],
  moduleDirectories: ['node_modules', '../../../app/frontend/src'],
  roots: ['<rootDir>'],
  transformIgnorePatterns: [
    'node_modules/(?!(axios)/)'
  ]
}; 