-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema match_score_project
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema match_score_project
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `match_score_project` DEFAULT CHARACTER SET latin1 ;
USE `match_score_project` ;

-- -----------------------------------------------------
-- Table `match_score_project`.`players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`players` (
  `id` INT(11) NOT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `country` VARCHAR(45) NOT NULL,
  `sport_club` VARCHAR(75) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`registered_users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`registered_users` (
  `id` INT(11) NOT NULL,
  `email` VARCHAR(85) NOT NULL,
  `pass` VARCHAR(45) NULL DEFAULT NULL,
  `players_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  INDEX `fk_registered_users_players_idx` (`players_id` ASC) VISIBLE,
  CONSTRAINT `fk_registered_users_players`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_project`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`admins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`admins` (
  `id` INT(11) NOT NULL,
  `registered_users_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_admins_registered_users1_idx` (`registered_users_id` ASC) VISIBLE,
  CONSTRAINT `fk_admins_registered_users1`
    FOREIGN KEY (`registered_users_id`)
    REFERENCES `match_score_project`.`registered_users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`tournaments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`tournaments` (
  `id` INT(11) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  `format` VARCHAR(45) NOT NULL,
  `price` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`match_result`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`match_result` (
  `id` INT NOT NULL,
  `player_won` INT NULL,
  `player_lost` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `match_score_project`.`matches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`matches` (
  `id` INT(11) NOT NULL,
  `date` DATETIME NOT NULL,
  `format` VARCHAR(45) NOT NULL,
  `time_limit` DATETIME NULL DEFAULT NULL,
  `score_limit` INT(11) NULL DEFAULT NULL,
  `tournaments_id` INT(11) NOT NULL,
  `match_result_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_matches_tournaments1_idx` (`tournaments_id` ASC) VISIBLE,
  INDEX `fk_matches_match_result1_idx` (`match_result_id` ASC) VISIBLE,
  CONSTRAINT `fk_matches_tournaments1`
    FOREIGN KEY (`tournaments_id`)
    REFERENCES `match_score_project`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_matches_match_result1`
    FOREIGN KEY (`match_result_id`)
    REFERENCES `match_score_project`.`match_result` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`players_has_matches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`players_has_matches` (
  `players_id` INT(11) NOT NULL,
  `matches_id` INT(11) NOT NULL,
  PRIMARY KEY (`players_id`, `matches_id`),
  INDEX `fk_players_has_matches_matches1_idx` (`matches_id` ASC) VISIBLE,
  INDEX `fk_players_has_matches_players1_idx` (`players_id` ASC) VISIBLE,
  CONSTRAINT `fk_players_has_matches_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `match_score_project`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_players_has_matches_players1`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_project`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`tournaments_has_players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`tournaments_has_players` (
  `tournaments_id` INT(11) NOT NULL,
  `players_id` INT(11) NOT NULL,
  PRIMARY KEY (`tournaments_id`, `players_id`),
  INDEX `fk_tournaments_has_players_players1_idx` (`players_id` ASC) VISIBLE,
  INDEX `fk_tournaments_has_players_tournaments1_idx` (`tournaments_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_has_players_players1`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_project`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_players_tournaments1`
    FOREIGN KEY (`tournaments_id`)
    REFERENCES `match_score_project`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_project`.`profile`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_project`.`profile` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `registered_users_id` INT(11) NOT NULL,
  `tournament_won` INT NULL,
  `tournamen_played` INT NULL,
  `matches_won` INT NULL,
  `matches_played` VARCHAR(45) NULL,
  `matches_lost` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_profile_registered_users1_idx` (`registered_users_id` ASC) VISIBLE,
  CONSTRAINT `fk_profile_registered_users1`
    FOREIGN KEY (`registered_users_id`)
    REFERENCES `match_score_project`.`registered_users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
