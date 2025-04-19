import { AuctionData, AuctionResult, AuctionValidator } from './types'
import { AuctionConstraints, bondBalanceRequiredForCurrentStake } from './constraints'
import { Debug } from './debug'

const logValidators = (validators: AuctionValidator[]) => {
  console.log('validators -----------------------------')
  for (const validator of validators) {
    console.log(validator.voteAccount, validator.revShare.totalPmpe, validator.auctionStake.marinadeMndeTargetSol, validator.auctionStake.marinadeSamTargetSol)
  }
  console.log('----------------------------- validators')
}

export class Auction {
  constructor (private data: AuctionData, private constraints: AuctionConstraints, private debug: Debug) { }

  setStakeUnstakePriorities () {
    // First sort by ascending totalPmpe for unstake priority
    this.data.validators.sort((a, b) => a.revShare.totalPmpe - b.revShare.totalPmpe)

    // Assign unstake priorities
    this.data.validators
      .filter(({ mndeEligible, samEligible }) => !mndeEligible && !samEligible)
      .forEach(validator => validator.unstakePriority = 0)

    let bondsMaxIndex = 0
    this.data.validators
      .filter(({ unstakePriority }) => Number.isNaN(unstakePriority))
      .map(validator => ({
        validator,
        bondBalanceDiff: ((validator.bondBalanceSol ?? 0) - bondBalanceRequiredForCurrentStake(validator)) / validator.marinadeActivatedStakeSol
      }))
      .filter(({ bondBalanceDiff }) => bondBalanceDiff < 0) // Infinity and NaN filtered out too
      .sort((a, b) => a.bondBalanceDiff - b.bondBalanceDiff)
      .forEach(({ validator }, index) => bondsMaxIndex = validator.unstakePriority = index + 1)

    this.data.validators
      .filter(({ unstakePriority }) => Number.isNaN(unstakePriority))
      .map(validator => ({
        validator,
        stakeDiff: validator.marinadeActivatedStakeSol <= 0 ?
          1 :
          (validator.auctionStake.marinadeMndeTargetSol + validator.auctionStake.marinadeSamTargetSol - validator.marinadeActivatedStakeSol) / validator.marinadeActivatedStakeSol
      }))
      .sort((a, b) => a.stakeDiff - b.stakeDiff)
      .forEach(({ validator }, index) => validator.unstakePriority = bondsMaxIndex + index + 1)

    // Then sort by descending totalPmpe for stake priority
    this.data.validators.sort((a, b) => b.revShare.totalPmpe - a.revShare.totalPmpe)

    // Assign stake priorities
    let currentGroupPmpe = NaN
    let currentStakePriority = 0
    this.data.validators.forEach(validator => {
      if (validator.revShare.totalPmpe === currentGroupPmpe) {
        validator.stakePriority = currentStakePriority
      } else {
        validator.stakePriority = ++currentStakePriority
        currentGroupPmpe = validator.revShare.totalPmpe
      }
    })
  }
} 