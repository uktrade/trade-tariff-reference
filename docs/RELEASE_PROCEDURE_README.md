# Trade tariff reference - Release procedure

To deploy the application a basic git flow approach has been taken
- Create a PR against develop with changes
- Once changes are approved and tests and style checks pass (circle-ci should run these on your behalf)
- Merge PR
- Once ready for deployment create a PR from develop to master like https://github.com/uktrade/trade-tariff-reference/pull/142
- Merged PR
- Create a Release tag https://github.com/uktrade/trade-tariff-reference/releases
- Then go to https://jenkins.ci.uktrade.io/view/Tariffs/job/tariff-reference/
- Click build with parameters
- Select required Environment 
- Select Git_Commit as develop if deploying to development
- Select Git_commit as master if deploying to staging or production
- Click build



